document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.content-card');
    const emptyState = document.getElementById('emptyState');

    function filterCategory(status) {
        let visibleCardsCount = 0;

        cards.forEach(card => {
            if (card.getAttribute('data-card-status') === status) {
                card.classList.add('show');
                visibleCardsCount++;
            } else {
                card.classList.remove('show');
            }
        });

        if (visibleCardsCount === 0) {
            emptyState.classList.add('show');
        } else {
            emptyState.classList.remove('show');
        }
    }

    buttons.forEach(button => {
        button.addEventListener('click', () => {
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            const targetStatus = button.getAttribute('data-status');
            filterCategory(targetStatus);
        });
    });

    // Filtra inicialmente as pendentes
    filterCategory('pending');
});
