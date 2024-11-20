from flask import Flask, jsonify, request, render_template
from flask_pymongo import PyMongo
from flask_jwt_extended import JWTManager, create_access_token,jwt_required,get_jwt_identity
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config["MONGO_URI"] = "mongodb://localhost:27017/abbatoir"  # Assurez-vous que ceci est correct
app.config['JWT_SECRET_KEY'] = 'votre_clé_secrète'
mongo = PyMongo(app)
jwt = JWTManager(app)

# Collection utilisateur
users_collection = mongo.db.users


@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data:
        print("Erreur : Aucune donnée reçue")  # Log d'erreur si aucune donnée n'est reçue
        return jsonify({"message": "Données non reçues"}), 400

    # Vérifie si l'email existe déjà
    if users_collection.find_one({"email": data['email']}):
        print("Erreur : Email déjà pris")  # Log d'erreur
        return jsonify({"message": "Email déjà pris"}), 409

    # Hache le mot de passe
    hashed_password = generate_password_hash(data['password'], method='pbkdf2:sha256')
    
    # Crée le nouvel utilisateur
    new_user = {
        "password": hashed_password,
        "email": data['email'],
        "nom": data['nom'],
        "prenom": data['prenom'],
        "telephone": data.get('telephone'),
        "adresse": data.get('adresse')
    }

    # Insère l'utilisateur dans MongoDB
    try:
        result = users_collection.insert_one(new_user)
        print(f"Utilisateur inséré avec l'ID : {result.inserted_id}")  # Log pour vérifier l'insertion
        return jsonify({"message": "Compte créé avec succès"}), 201
    except Exception as e:
        print(f"Erreur d'insertion dans MongoDB : {e}")  # Log d'erreur d'insertion
        return jsonify({"message": "Erreur lors de la création du compte"}), 500

# Route de soumission de connexion
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    identifier = data.get("identifier")
    password = data.get("password")

    # Rechercher par email ou par téléphone
    user = users_collection.find_one({"$or": [{"email": identifier}, {"telephone": identifier}]})
    
    if user and check_password_hash(user['password'], password):
        # Inclure le nom et le prénom dans le jeton
        access_token = create_access_token(identity={"user_id": str(user['_id']), "nom": user['nom'], "prenom": user['prenom']})
        return jsonify(access_token=access_token), 200
    return jsonify({"message": "Email/téléphone ou mot de passe incorrect"}), 401


@app.route('/dashboard', methods=['GET'])
def serve_dashboard():
    # Cette route sert le tableau de bord sans nécessiter de JWT
    return render_template('dashboard.html')

@app.route('/dashboard_data', methods=['GET'])
@jwt_required()  # Cette route nécessite un jeton JWT
def dashboard_data():
    # Récupérer le nom et le prénom depuis le jeton JWT
    identity = get_jwt_identity()
    nom = identity.get("nom")
    prenom = identity.get("prenom")
    
    # Message de bienvenue avec nom et prénom
    data = {"message": f"Bienvenue sur votre tableau de bord, {nom} {prenom}"}
    return jsonify(data)

# Route pour servir la page de connexion
@app.route('/login', methods=['GET'])
def serve_login():
    return render_template('login.html')

# Route pour servir la page d'inscription
@app.route('/register', methods=['GET'])
def serve_register():
    return render_template('register.html')

if __name__ == '__main__':
    app.run(debug=True)
