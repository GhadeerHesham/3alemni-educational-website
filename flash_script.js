let flashcards = [];
let index = 0;
let flipped = false;

const flashcard = document.getElementById("flashcard");
const flashcardText = document.getElementById("flashcard-text");
const flashcardAnswer = document.getElementById("flashcard-answer");
const pdfUpload = document.getElementById("pdf-upload");

// Load flashcards from server
async function loadFlashcards(text) {
    const response = await fetch("http://127.0.0.1:5000/generate_flashcards", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ text: text, num_flashcards_limit: 5 })
    });

    const data = await response.json();
    flashcards = data.flashcards;
    index = 0;
    flipped = false;
    showFlashcard();
}

// Show the current flashcard
function showFlashcard() {
    if (index < flashcards.length) {
        flashcardText.innerHTML = `<strong>Question:</strong> ${flashcards[index].question}`;
        flashcardAnswer.innerHTML = `<strong>Answer:</strong> ${flashcards[index].answer}`;
        flashcard.classList.remove("flipped");
        flashcard.style.display = "block";
    } else {
        flashcardText.innerHTML = "No more flashcards.";
        flashcardAnswer.innerHTML = "";
        flashcard.classList.remove("flipped");
    }
}

// Flip and go to next
function flipCard() {
    flashcard.classList.toggle("flipped");
    flipped = !flipped;

    // When flipped back, go to next card
    if (!flipped) {
        index++;
        setTimeout(showFlashcard, 300); // wait for flip animation
    }
}

// Handle PDF Upload and extract text using pdf.js
pdfUpload.addEventListener("change", async function (event) {
    const file = event.target.files[0];
    if (file && file.type === "application/pdf") {
        const reader = new FileReader();

        reader.onload = async function () {
            const typedArray = new Uint8Array(reader.result);
            const pdf = await pdfjsLib.getDocument(typedArray).promise;

            let fullText = "";
            for (let i = 1; i <= pdf.numPages; i++) {
                const page = await pdf.getPage(i);
                const content = await page.getTextContent();
                const strings = content.items.map(item => item.str);
                fullText += strings.join(" ") + "\n";
            }

            loadFlashcards(fullText);
        };

        reader.readAsArrayBuffer(file);
    } else {
        alert("Please upload a valid PDF file.");
    }
});

// Optional: Load flashcards with static text on page load
// window.onload = () => {
//     loadFlashcards("2+2=4, 4+2=6, 6+2=8, 8+2=10, 10+2=12");
// };
