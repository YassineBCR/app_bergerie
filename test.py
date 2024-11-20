from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta

app = FastAPI()

SECRET_KEY = "your-secret-key"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class Item(BaseModel):
    id: int
    name: str
    description: Optional[str] = None

fake_db = {
    1: {"name": "Item1", "description": "Description for Item1"},
    2: {"name": "Item2", "description": "Description for Item2"}
}

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
    return user_id

@app.get("/items/{item_id}", response_model=Item)
async def read_item(item_id: int, user: str = Depends(get_current_user)):
    item = fake_db.get(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return Item(id=item_id, name=item["name"], description=item.get("description"))

@app.put("/items/{item_id}", response_model=Item)
async def update_item(item_id: int, item: Item, user: str = Depends(get_current_user)):
    if item_id not in fake_db:
        raise HTTPException(status_code=404, detail="Item not found")
    fake_db[item_id] = item.dict()
    return item

@app.delete("/items/{item_id}")
async def delete_item(item_id: int, user: str = Depends(get_current_user)):
    if item_id in fake_db:
        del fake_db[item_id]
        return {"detail": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")

@app.post("/token")
async def login():
    access_token = create_access_token(data={"sub": "user_id"})
    return {"access_token": access_token, "token_type": "bearer"}
