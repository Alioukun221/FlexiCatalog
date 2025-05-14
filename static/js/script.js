// register.js
document.addEventListener('DOMContentLoaded', function() {
    const registerForm = document.getElementById('registerForm');
    
    if (registerForm) {
        registerForm.addEventListener('submit', function(e) {
            const password = document.getElementById('password').value;
            const confirmPassword = document.getElementById('confirm_password').value;
            
            if (password !== confirmPassword) {
                e.preventDefault();
                
                // Créer un message d'erreur
                const messageDiv = document.createElement('div');
                messageDiv.className = 'message error';
                messageDiv.textContent = 'Les mots de passe ne correspondent pas';
                
                // Rechercher s'il y a déjà des messages
                const messagesContainer = document.querySelector('.messages');
                
                if (messagesContainer) {
                    // Supprimer les anciens messages d'erreur de mot de passe
                    const oldPasswordErrors = messagesContainer.querySelectorAll('.message.error');
                    oldPasswordErrors.forEach(error => {
                        if (error.textContent.includes('mot de passe')) {
                            error.remove();
                        }
                    });
                    
                    // Ajouter le nouveau message
                    messagesContainer.appendChild(messageDiv);
                } else {
                    // Créer un conteneur de messages
                    const newMessagesContainer = document.createElement('div');
                    newMessagesContainer.className = 'messages';
                    newMessagesContainer.appendChild(messageDiv);
                    
                    // Insérer le conteneur après le titre h1
                    const h1 = document.querySelector('h1');
                    h1.insertAdjacentElement('afterend', newMessagesContainer);
                }
                
                // Mettre en surbrillance les champs de mot de passe
                document.getElementById('password').style.borderColor = '#d63031';
                document.getElementById('confirm_password').style.borderColor = '#d63031';
            }
        });
        
        // Réinitialiser les styles de bordure lorsque l'utilisateur commence à taper
        document.getElementById('password').addEventListener('input', function() {
            this.style.borderColor = '';
            document.getElementById('confirm_password').style.borderColor = '';
        });
        
        document.getElementById('confirm_password').addEventListener('input', function() {
            this.style.borderColor = '';
            document.getElementById('password').style.borderColor = '';
        });
    }
});