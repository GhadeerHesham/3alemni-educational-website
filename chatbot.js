// Chatling Configuration
window.chtlConfig = {
    chatbotId: "3615595289",
    display: "page_inline"
};

// Dynamically load Chatling script
window.addEventListener("DOMContentLoaded", () => {
    const chatlingDiv = document.createElement("div");
    chatlingDiv.id = "chatling-inline-bot";
    chatlingDiv.style.width = "100%";
    chatlingDiv.style.height = "100%";

    const chatWindow = document.getElementById("chat-window");
    if (chatWindow) {
        chatWindow.innerHTML = ""; // Clear any static content
        chatWindow.appendChild(chatlingDiv);
    }

    const script = document.createElement("script");
    script.async = true;
    script.dataset.id = "3615595289";
    script.dataset.display = "page_inline";
    script.id = "chatling-embed-script";
    script.type = "text/javascript";
    script.src = "https://chatling.ai/js/embed.js";

    document.body.appendChild(script);
});
