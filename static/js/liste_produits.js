
    document.addEventListener('DOMContentLoaded', function () {
        // Mise à jour de l'affichage du prix
        const prixSlider = document.getElementById('prix');
        const prixValue = document.getElementById('prix-value');

        prixSlider.addEventListener('input', function () {
            prixValue.textContent = this.value + 'FCFA';
        });

        // Filtrage des produits
        const categorieSelect = document.getElementById('categorie');
        const marqueSelect = document.getElementById('marque');

        function filterProducts() {
            const categorie = categorieSelect.value;
            const marque = marqueSelect.value;
            const prixMax = prixSlider.value;

            // Ici, vous pouvez ajouter la logique de filtrage AJAX
            console.log('Filtres:', { categorie, marque, prixMax });
        }

        categorieSelect.addEventListener('change', filterProducts);
        marqueSelect.addEventListener('change', filterProducts);
        prixSlider.addEventListener('change', filterProducts);
    });
