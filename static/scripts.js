async function registerUser() {
    const nom = document.getElementById("registerNom").value;
    const prenom = document.getElementById("registerPrenom").value;
    const email = document.getElementById("registerEmail").value;
    const telephone = document.getElementById("registerTelephone").value;
    const adresse = document.getElementById("registerAdresse").value;
    const password = document.getElementById("registerPassword").value;
    const confirmPassword = document.getElementById("confirmPassword").value;

    if (password !== confirmPassword) {
        alert("Les mots de passe ne correspondent pas.");
        return;
    }

    const response = await fetch('/register', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            nom: nom,
            prenom: prenom,
            email: email,
            telephone: telephone,
            adresse: adresse,
            password: password
        })
    });

    const result = await response.json();
    if (response.ok) {
        alert("Compte créé avec succès. Vous pouvez maintenant vous connecter.");
    } else {
        alert(result.message);
    }
}

async function loginUser() {
    const identifier = document.getElementById("loginIdentifier").value;
    const password = document.getElementById("loginPassword").value;

    const response = await fetch('/login', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({ identifier: identifier, password: password })
    });

    const result = await response.json();
    if (response.ok) {
        // Enregistrer le jeton dans le stockage local
        localStorage.setItem('access_token', result.access_token);
        
        // Redirection vers le tableau de bord
        window.location.href = "/dashboard";
    } else {
        alert(result.message);
    }
}


function togglePasswordVisibility() {
    const registerPassword = document.getElementById("registerPassword");
    const confirmPassword = document.getElementById("confirmPassword");
    const loginPassword = document.getElementById("loginPassword");

    // Vérifiez si le type est "password" et basculez à "text" ou inversement
    const isPasswordVisible = registerPassword ? registerPassword.type === "password" : loginPassword.type === "password";

    if (registerPassword) {
        registerPassword.type = isPasswordVisible ? "text" : "password";
    }
    if (confirmPassword) {
        confirmPassword.type = isPasswordVisible ? "text" : "password";
    }
    if (loginPassword) {
        loginPassword.type = isPasswordVisible ? "text" : "password";
    }
}
