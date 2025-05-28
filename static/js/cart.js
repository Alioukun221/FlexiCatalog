//static/js/cart.js
 document.addEventListener('DOMContentLoaded', function() {
      //Mise à jour dynamique du panier
      function updateCartCounter() {
          fetch('/cart/api/count/')
              .then(response => response.json())
              .then(data => {
                  const counters = document.querySelectorAll('.cart-counter');
                  counters.forEach(counter => {
                     counter.textContent = data.count;
                  });
              });
      }

      //Animation lors de l'ajout au panier
     function animateCart() {
         const cartIcons = document.querySelectorAll('.fa-shopping-cart');
         cartIcons.forEach(icon => {
             icon.classList.add('cart-animate');
             setTimeout(() => {
                 icon.classList.remove('cart-animate');
             }, 500);
         });
     }

      //Affichage des messages
     function showMessage(message, type = 'success') {
         const messageDiv = document.createElement('div');
         messageDiv.className = `alert alert-${type} alert-message`;
         messageDiv.textContent = message;
         document.body.appendChild(messageDiv);
        
         setTimeout(() => {
             messageDiv.classList.add('show');
         }, 100);
        
         setTimeout(() => {
             messageDiv.classList.remove('show');
             setTimeout(() => messageDiv.remove(), 300);
         }, 3000);
     }

    //Exposer les fonctions globalement
     window.cartUtils = {
         updateCartCounter,
         animateCart,
         showMessage
     };
 });