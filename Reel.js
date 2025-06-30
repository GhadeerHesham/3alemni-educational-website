document.addEventListener("DOMContentLoaded", function () {
  const generateBtn = document.querySelector(".generate-btn");
  const fileInput = document.getElementById("pdfInput");
  const reelsScroll = document.querySelector(".reels-scroll");
  const loadingMessage = document.getElementById("loading-message");

  generateBtn.addEventListener("click", convertToReel);

  // Load reels on page load
  loadReels();

  async function loadReels() {
    try {
      const response = await fetch("http://127.0.0.1:5000/list-reels");
      const videoUrls = await response.json();

      reelsScroll.innerHTML = ""; // Clear previous videos

      videoUrls.forEach((url) => {
        const fileName = url.split("/").pop();

        const reel = document.createElement("div");
        reel.className = "reel";

        reel.innerHTML = `
          <div class="video-container">
            <video class="reel-video" src="${url}" autoplay loop muted controls></video>
            <div class="">
              <p><strong>${fileName}</strong></p>
            </div>
          </div>
          <div class="reel-actions">
            <button class="action-btn"><i class="fas fa-heart"></i></button>
            <button class="action-btn"><i class="fas fa-comment"></i></button>
            <button class="action-btn"><i class="fas fa-share"></i></button>
          </div>
        `;

        reelsScroll.appendChild(reel);
      });
    } catch (err) {
      console.error("Failed to load reels:", err);
    }
  }

  async function convertToReel() {
    const file = fileInput.files[0];
    if (!file) {
      alert("Please upload a file.");
      return;
    }

    const formData = new FormData();
    formData.append("file", file);
    formData.append("lang", "en");

    try {
      loadingMessage.style.display = "block";

      const response = await fetch("http://127.0.0.1:5000/generate-reel", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) {
        const result = await response.json();
        alert("Error: " + result.error);
        loadingMessage.style.display = "none";
        return;
      }

      // Wait a bit to let the file be saved to disk
      await new Promise((r) => setTimeout(r, 1000));

      // Refresh video list
      await loadReels();

    } catch (error) {
      alert("An error occurred: " + error.message);
    } finally {
      loadingMessage.style.display = "none";
    }
  }
});
