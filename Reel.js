// Function to toggle play/pause
function togglePlayPause(video, button) {
    if (video.paused) {
        video.play();
        button.classList.add("playing"); // Hide play button
    } else {
        video.pause();
        button.classList.remove("playing"); // Show play button
    }
}

// Function to pause all videos except the one in view
function pauseAllVideosExcept(currentVideo) {
    document.querySelectorAll(".reel-video").forEach((video) => {
        if (video !== currentVideo && !video.paused) {
            video.pause();
            const button = video.closest(".video-container").querySelector(".play-pause-btn");
            button.classList.remove("playing"); // Show play button for paused videos
        }
    });
}

// Add event listeners to all play/pause buttons
document.querySelectorAll(".play-pause-btn").forEach((button) => {
    const video = button.closest(".video-container").querySelector(".reel-video");

    // Toggle play/pause on button click
    button.addEventListener("click", (event) => {
        event.stopPropagation(); // Prevent event from bubbling to the video container
        togglePlayPause(video, button);
    });

    // Toggle play/pause when clicking anywhere in the video container
    const videoContainer = button.closest(".video-container");
    videoContainer.addEventListener("click", () => {
        togglePlayPause(video, button); // Toggle play/pause
    });

    // Show play button when video is paused
    video.addEventListener("pause", () => {
        button.classList.remove("playing");
    });

    // Hide play button when video starts playing
    video.addEventListener("play", () => {
        button.classList.add("playing");
    });

    // Show play button when video ends
    video.addEventListener("ended", () => {
        button.classList.remove("playing");
    });
});

// Pause videos when scrolling
const reelsScroll = document.querySelector(".reels-scroll");
reelsScroll.addEventListener("scroll", () => {
    // Get the currently visible reel
    const visibleReel = Array.from(document.querySelectorAll(".reel")).find((reel) => {
        const rect = reel.getBoundingClientRect();
        return rect.top >= 0 && rect.bottom <= window.innerHeight;
    });

    if (visibleReel) {
        const visibleVideo = visibleReel.querySelector(".reel-video");
        pauseAllVideosExcept(visibleVideo); // Pause all videos except the visible one
    }
});
// comment nada