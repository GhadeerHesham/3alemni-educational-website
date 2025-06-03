// Function to toggle play/pause
function togglePlayPause(video, button) {
    if (video.paused) {
        video.play();
        button.classList.add("playing");
    } else {
        video.pause();
        button.classList.remove("playing");
    }
}

// Function to pause all videos except the one in view
function pauseAllVideosExcept(currentVideo) {
    document.querySelectorAll(".reel-video").forEach((video) => {
        if (video !== currentVideo && !video.paused) {
            video.pause();
            const button = video.closest(".video-container").querySelector(".play-pause-btn");
            button.classList.remove("playing");
        }
    });
}

// Add event listeners to all play/pause buttons
document.querySelectorAll(".play-pause-btn").forEach((button) => {
    const video = button.closest(".video-container").querySelector(".reel-video");

    button.addEventListener("click", (event) => {
        event.stopPropagation();
        togglePlayPause(video, button);
    });

    const videoContainer = button.closest(".video-container");
    videoContainer.addEventListener("click", () => {
        togglePlayPause(video, button);
    });

    video.addEventListener("pause", () => {
        button.classList.remove("playing");
    });

    video.addEventListener("play", () => {
        button.classList.add("playing");
    });

    video.addEventListener("ended", () => {
        button.classList.remove("playing");
    });
});

// Pause videos when scrolling
const reelsScroll = document.querySelector(".reels-scroll");
reelsScroll.addEventListener("scroll", () => {
    const visibleReel = Array.from(document.querySelectorAll(".reel, .generated-reel")).find((reel) => {
        const rect = reel.getBoundingClientRect();
        return rect.top >= 0 && rect.bottom <= window.innerHeight;
    });

    if (visibleReel) {
        const visibleVideo = visibleReel.querySelector(".reel-video");
        if (visibleVideo) {
            pauseAllVideosExcept(visibleVideo);
        }
    }
});

// Function to convert PPT/PPTX to PDF using ConvertAPI
async function convertPptToPdf(file) {
    const apiSecret = "u2s5c5aql6Sv6DuMBEfLFhvgvwSFEjqp"; // Replace with your ConvertAPI Sandbox or Production Token
    console.log("Starting PPT to PDF conversion...");
    const formData = new FormData();
    formData.append("File", file);
    try {
        const response = await fetch("https://v2.convertapi.com/convert/pptx/to/pdf?Secret=" + apiSecret, {
            method: "POST",
            body: formData,
        });
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(`PPT to PDF conversion failed: ${errorData.Message || response.statusText}`);
        }
        console.log("PPT converted to PDF successfully");
        return await response.blob();
    } catch (error) {
        console.error("PPT conversion error:", error);
        alert(`Failed to convert PPT to PDF: ${error.message}. Please try again or upload a PDF directly.`);
        throw error;
    }
}

// Function to convert PDF or PPT to reel
async function convertToReel() {
    console.log("convertToReel function triggered");
    const pdfInput = document.getElementById("pdfInput");
    const reelsScroll = document.querySelector(".reels-scroll");

    if (!pdfInput.files.length) {
        console.log("No file selected");
        alert("Please upload a PDF or PPT file.");
        return;
    }

    let file = pdfInput.files[0];
    const fileType = file.type;
    console.log("Selected file type:", fileType);

    // Convert PPT/PPTX to PDF if necessary
    if (fileType === "application/vnd.ms-powerpoint" || fileType === "application/vnd.openxmlformats-officedocument.presentationml.presentation") {
        console.log("Converting PPT/PPTX to PDF...");
        try {
            file = await convertPptToPdf(file);
        } catch (error) {
            console.log("PPT conversion failed, stopping process");
            return;
        }
    } else if (fileType !== "application/pdf") {
        console.log("Invalid file type:", fileType);
        alert("Please upload a valid PDF or PPT file.");
        return;
    }

    const fileReader = new FileReader();
    console.log("Reading file as ArrayBuffer...");

    // Initialize CCapture for video export
    const capturer = new CCapture({ format: "webm", framerate: 30 });
    capturer.start();
    console.log("CCapture started");

    fileReader.onload = async function () {
        try {
            console.log("FileReader onload triggered");
            const typedArray = new Uint8Array(this.result);
            const pdf = await pdfjsLib.getDocument(typedArray).promise;
            console.log(`PDF loaded with ${pdf.numPages} pages`);

            // Clear existing generated reels
            document.querySelectorAll(".generated-reel").forEach((reel) => reel.remove());
            console.log("Cleared existing generated reels");

            for (let pageNum = 1; pageNum <= pdf.numPages; pageNum++) {
                console.log(`Processing page ${pageNum}`);
                const page = await pdf.getPage(pageNum);
                const textContent = await page.getTextContent();
                const text = textContent.items.map((item) => item.str).join(" ").substring(0, 100);
                console.log(`Extracted text for page ${pageNum}:`, text);

                // Create canvas for rendering PDF page
                const viewport = page.getViewport({ scale: 1.0 });
                const canvas = document.createElement("canvas");
                const context = canvas.getContext("2d");
                canvas.width = viewport.width;
                canvas.height = viewport.height;
                await page.render({ canvasContext: context, viewport }).promise;
                console.log(`Rendered page ${pageNum} to canvas`);

                // Create reel element
                const reel = document.createElement("div");
                reel.className = "generated-reel";
                reel.appendChild(canvas);

                // Add animated text
                const textDiv = document.createElement("div");
                textDiv.className = "slide-text";
                textDiv.textContent = text || `Page ${pageNum}`;
                reel.appendChild(textDiv);
                console.log(`Created reel for page ${pageNum}`);

                reelsScroll.appendChild(reel);

                // Animate the reel
                reel.classList.add("active");
                gsap.fromTo(
                    canvas,
                    { opacity: 0, scale: 0.8 },
                    { opacity: 1, scale: 1, duration: 1, ease: "power2.out" }
                );
                gsap.fromTo(
                    textDiv,
                    { opacity: 0, y: 50, rotation: 5 },
                    { opacity: 1, y: 0, rotation: 0, duration: 1, delay: 0.5, ease: "elastic.out(1, 0.5)" }
                );
                console.log(`Animating page ${pageNum}`);

                // Optional: Add text-to-speech
                const utterance = new SpeechSynthesisUtterance(text || `Page ${pageNum}`);
                utterance.rate = 1.2;
                window.speechSynthesis.speak(utterance);

                // Capture frame for video
                capturer.capture(reelsScroll);
                console.log(`Captured frame for page ${pageNum}`);

                // Wait for animation to complete
                await new Promise((resolve) => setTimeout(resolve, 3000));

                gsap.to(canvas, { opacity: 0, scale: 0.8, duration: 1, ease: "power2.in" });
                gsap.to(textDiv, { opacity: 0, y: -50, duration: 1, ease: "power2.in" });
                reel.classList.remove("active");
                console.log(`Finished animation for page ${pageNum}`);

                // Capture frame for transition
                capturer.capture(reelsScroll);

                await new Promise((resolve) => setTimeout(resolve, 1000));
            }

            // Stop and save video
            capturer.stop();
            capturer.save();
            console.log("Video capture stopped and saved");
            alert("Reel generation complete! Check the downloaded video.");
        } catch (error) {
            console.error("Error processing PDF:", error);
            alert(`Error generating reel: ${error.message}. Please try again with a valid PDF or PPT file.`);
        }
    };

    fileReader.onerror = function () {
        console.error("FileReader error:", fileReader.error);
        alert("Error reading file. Please ensure the file is valid and try again.");
    };

    fileReader.readAsArrayBuffer(file);
}