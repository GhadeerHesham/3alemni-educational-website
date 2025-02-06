const flashcards = [
    { question: "What is the capital of France?", answer: "Paris" },
    { question: "What is 2 + 2?", answer: "4" },
    { question: "What is the largest planet in the solar system?", answer: "Jupiter" }
];

let index = 0;
let flipped = false;
const flashcard = document.getElementById("flashcard");
const flashcardText = document.getElementById("flashcard-text");
const flashcardAnswer = document.getElementById("flashcard-answer");

function flipCard() {
    flashcard.classList.toggle("flipped");
    flipped = !flipped;
    if (!flipped) {
        index++;
        if (index < flashcards.length) {
            flashcardText.innerHTML = `<strong>Question:</strong> ${flashcards[index].question}`;
            flashcardAnswer.innerHTML = `<strong>Answer:</strong> ${flashcards[index].answer}`;
        } else {
            flashcard.style.display = "none";
        }
    }
}