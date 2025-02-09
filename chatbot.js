// Chatling Configuration
window.chtlConfig = {
    chatbotId: "3615595289",
    display: "page_inline"
};

// Load Chatling Embed Script
const script = document.createElement("script");
script.async = true;
script.dataset.id = "3615595289";
script.id = "chatling-embed-script";
script.dataset.display = "page_inline";
script.type = "text/javascript";
script.src = "https://chatling.ai/js/embed.js";

// Append the script to the document body
document.body.appendChild(script);