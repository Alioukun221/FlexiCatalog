
    document.addEventListener('DOMContentLoaded', function() {
        const passwordInput = document.querySelector('input[name="new_password"]');
        const strengthMeter = document.querySelector('.password-strength-meter');
        
        passwordInput.addEventListener('input', function() {
            const val = passwordInput.value;
            let strength = 0;
            
            // Règles pour évaluer la force du mot de passe
            if (val.length >= 8) strength += 1;
            if (val.match(/[a-z]/) && val.match(/[A-Z]/)) strength += 1;
            if (val.match(/\d/)) strength += 1;
            if (val.match(/[^a-zA-Z\d]/)) strength += 1;
            
            // Mettre à jour l'indicateur visuel
            strengthMeter.className = 'password-strength-meter';
            if (strength === 0) {
                strengthMeter.style.width = '0';
            } else if (strength === 1) {
                strengthMeter.classList.add('weak');
            } else if (strength === 2) {
                strengthMeter.classList.add('medium');
            } else if (strength === 3) {
                strengthMeter.classList.add('strong');
            } else {
                strengthMeter.classList.add('very-strong');
            }
        });
    });