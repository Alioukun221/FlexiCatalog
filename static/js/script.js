/**
 * Fonction pour basculer l'affichage du mot de passe
 * @param {string} fieldId - L'ID du champ de mot de passe
 */
function togglePassword(fieldId) {
    const field = document.getElementById(fieldId);
    const button = field.nextElementSibling;
    
    if (field.type === "password") {
        field.type = "text";
        button.textContent = "🔒"; // Changer l'icône quand le mot de passe est visible
    } else {
        field.type = "password";
        button.textContent = "👁️"; // Remettre l'icône originale
    }
}

/**
 * Validation du formulaire
 */
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    
    form.addEventListener('submit', function(event) {
        event.preventDefault();
        
        // Récupération des valeurs
        const name = document.getElementById('fullname').value.trim();
        const email = document.getElementById('email').value.trim();
        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirm-password').value;
        const agreeTerms = document.getElementById('agree-terms').checked;
        
        // Validation simple
        if (name === '') {
            alert('Please enter your name');
            return;
        }
        
        if (email === '') {
            alert('Please enter your email');
            return;
        }
        
        if (!isValidEmail(email)) {
            alert('Please enter a valid email address');
            return;
        }
        
        if (password === '') {
            alert('Please enter a password');
            return;
        }
        
        if (password !== confirmPassword) {
            alert('Passwords do not match');
            return;
        }
        
        if (!agreeTerms) {
            alert('You must agree to the Terms & Conditions');
            return;
        }
        
        // Si tout est valide, on pourrait soumettre le formulaire ici
        alert('Form submitted successfully!');
        // form.submit();
    });
    
    /**
     * Validation simple d'email
     * @param {string} email - L'adresse email à valider
     * @returns {boolean} - True si l'email est valide
     */
    function isValidEmail(email) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return emailRegex.test(email);
    }
});