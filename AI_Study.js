document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('ai-study-form');

    form.addEventListener('submit', function(event) {
        event.preventDefault(); // Prevent the form from submitting traditionally

        // Get the selected option
        const selectedOption = document.querySelector('input[name="option"]:checked').value;

        // Redirect based on the selected option
        if (selectedOption === 'flashcards') {
            window.location.href = 'flashcards.html'; // Redirect to flashcards page
        } else if (selectedOption === 'reels') {
            window.location.href = 'Reels.html'; // Redirect to reels page
        }
    });
});