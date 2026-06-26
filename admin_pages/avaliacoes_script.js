document.addEventListener('DOMContentLoaded', () => {
    const buttons = document.querySelectorAll('.filter-btn');
    const cards = document.querySelectorAll('.content-card');
    const emptyState = document.getElementById('emptyState');

    // Função que gere o display dos cards
    function filterCategory(status) {
        let visibleCardsCount = 0;

        cards.forEach(card => {
            // Se o atributo do card for idêntico ao filtro, adiciona a classe .show
            if (card.getAttribute('data-card-status') === status) {
                card.classList.add('show');
                visibleCardsCount++;
            } else {
                card.classList.remove('show');
            }
        });

        // Caso a categoria selecionada não tenha cards, ativa a mensagem de feedback
        if (visibleCardsCount === 0) {
            emptyState.classList.add('show');
        } else {
            emptyState.classList.remove('show');
        }
    }

    // Adiciona o evento de clique a cada botão de filtro
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove a classe ativa anterior e define o botão clicado como ativo
            buttons.forEach(btn => btn.classList.remove('active'));
            button.classList.add('active');

            // Captura o status alvo (pending, approved, cancelled)
            const targetStatus = button.getAttribute('data-status');
            filterCategory(targetStatus);
        });
    });

    // Estado inicial: Renderiza os elementos 'pendentes' por padrão
    filterCategory('pending');
});