// Reel.js - Complete Working Version

// Initialize PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = 
    "https://cdnjs.cloudflare.com/ajax/libs/pdf.js/2.16.105/pdf.worker.min.js";

// Main function to convert PDF to reels
async function convertToReel() {
    try {
        console.log("Starting PDF to reel conversion...");
        
        const pdfInput = document.getElementById("pdfInput");
        const reelsScroll = document.querySelector(".reels-scroll");
        
        if (!pdfInput.files.length) {
            alert("Please upload a PDF file.");
            return;
        }

        const file = pdfInput.files[0];
        console.log("Selected file:", file.name);

        // Show loading state
        reelsScroll.innerHTML = '<div class="loading">Processing PDF... <div class="spinner"></div></div>';
        
        const fileReader = new FileReader();

        fileReader.onload = async function() {
            try {
                console.log("File read successfully, processing PDF...");
                const typedArray = new Uint8Array(this.result);
                
                // Load PDF document
                const pdf = await pdfjsLib.getDocument(typedArray).promise;
                console.log(`PDF loaded successfully with ${pdf.numPages} pages`);
                
                // Clear previous content
                reelsScroll.innerHTML = '';
                
                // Process each page
                for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                    console.log(`Processing page ${pageNum}`);
                    
                    const page = await pdf.getPage(pageNum);
                    const viewport = page.getViewport({ scale: 1.0 });
                    
                    // Create canvas for PDF rendering
                    const canvas = document.createElement("canvas");
                    canvas.className = "pdf-page";
                    const context = canvas.getContext("2d");
                    
                    // Set canvas dimensions
                    const outputScale = window.devicePixelRatio || 1;
                    canvas.width = Math.floor(viewport.width * outputScale);
                    canvas.height = Math.floor(viewport.height * outputScale);
                    
                    // Adjust for high DPI displays
                    context.scale(outputScale, outputScale);
                    
                    // Render PDF page
                    await page.render({
                        canvasContext: context,
                        viewport: viewport
                    }).promise;
                    console.log(`Page ${pageNum} rendered successfully`);
                    
                    // Extract text (first 100 chars)
                    const textContent = await page.getTextContent();
                    const pageText = textContent.items.map(item => item.str).join(' ').trim();
                    const shortText = pageText.substring(0, 100) + (pageText.length > 100 ? "..." : "");
                    
                    // Create reel container
                    const reelContainer = document.createElement("div");
                    reelContainer.className = "generated-reel";
                    
                    // Add elements to container
                    reelContainer.appendChild(canvas);
                    
                    if (shortText) {
                        const textElement = document.createElement("div");
                        textElement.className = "pdf-text";
                        textElement.textContent = shortText;
                        reelContainer.appendChild(textElement);
                        
                        // Optional: Add text-to-speech
                        if (window.speechSynthesis) {
                            const utterance = new SpeechSynthesisUtterance(shortText);
                            utterance.rate = 0.9;
                            window.speechSynthesis.speak(utterance);
                        }
                    }
                    
                    reelsScroll.appendChild(reelContainer);
                    
                    // Add simple animation if GSAP is available
                    if (window.gsap) {
                        gsap.from(reelContainer, {
                            opacity: 0,
                            y: 50,
                            duration: 0.5,
                            delay: pageNum * 0.1
                        });
                    }
                }
                
                console.log("All pages processed successfully");
                
            } catch (error) {
                console.error("PDF processing error:", error);
                reelsScroll.innerHTML = `
                    <div class="error">
                        <h3>Error Processing PDF</h3>
                        <p>${error.message}</p>
                        <p>Please try a different PDF file.</p>
                    </div>
                `;
            }
        };
        
        fileReader.onerror = function() {
            console.error("File reading error:", fileReader.error);
            reelsScroll.innerHTML = `
                <div class="error">
                    <h3>Error Reading File</h3>
                    <p>The file could not be read.</p>
                    <p>Please try a different file.</p>
                </div>
            `;
        };
        
        fileReader.readAsArrayBuffer(file);
        
    } catch (error) {
        console.error("Conversion error:", error);
        alert(`Error: ${error.message}`);
    }
}

// Play/Pause functionality for videos (if you add videos later)
function setupVideoControls() {
    document.querySelectorAll(".reel-video").forEach(video => {
        const container = video.closest(".video-container");
        const button = container?.querySelector(".play-pause-btn");
        
        if (button) {
            button.addEventListener("click", () => togglePlayPause(video, button));
        }
    });
}

function togglePlayPause(video, button) {
    if (video.paused) {
        video.play();
        button?.classList.add("playing");
    } else {
        video.pause();
        button?.classList.remove("playing");
    }
}

// Initialize when DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
    console.log("Reels page loaded");
    
    // Setup event listeners
    const generateBtn = document.querySelector(".upload-container button");
    if (generateBtn) {
        generateBtn.addEventListener("click", convertToReel);
    }
    
    // Setup any existing video controls
    setupVideoControls();
});