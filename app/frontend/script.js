const API_URL = "http://127.0.0.1:8000";

/* =========================
   Upload Document
========================= */

async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const status = document.getElementById("uploadStatus");

    if (!fileInput.files.length) return;

    status.innerText = "Indexing document...";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    const response = await fetch(`${API_URL}/upload`, {
        method: "POST",
        body: formData
    });

    const data = await response.json();

    status.innerText = data.status;

    document.getElementById("docName").innerText =
        `Document: ${fileInput.files[0].name}`;
}

/* =========================
   Send Message
========================= */

async function sendMessage() {
    const input = document.getElementById("questionInput");
    const chatContainer = document.getElementById("chatContainer");
    const topK = document.getElementById("topK").value;

    const question = input.value.trim();
    if (!question) return;

    addMessage(question, "user");
    input.value = "";

    // Typing indicator
    const thinkingWrapper = document.createElement("div");
    thinkingWrapper.classList.add("message-wrapper", "bot");

    const thinking = document.createElement("div");
    thinking.classList.add("message", "bot", "typing");

    thinking.innerHTML = `
      <span></span>
      <span></span>
      <span></span>
    `;

    thinkingWrapper.appendChild(thinking);
    chatContainer.appendChild(thinkingWrapper);

    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: "smooth"
    });

    const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            question: question,
            top_k: parseInt(topK)
        })
    });

    const data = await response.json();

    chatContainer.removeChild(thinkingWrapper);

    addMessage(data.answer, "bot", data);
}

/* =========================
   Add Message to UI
========================= */

function addMessage(text, type, metadata = null) {
    const chatContainer = document.getElementById("chatContainer");

    const messageWrapper = document.createElement("div");
    messageWrapper.classList.add("message-wrapper", type);

    const message = document.createElement("div");
    message.classList.add("message", type);
    message.innerText = text;

    messageWrapper.appendChild(message);

    if (metadata && type === "bot") {

        // Confidence badge
        const confidence = document.createElement("div");
        confidence.classList.add("confidence");
        confidence.innerText = `Confidence: ${metadata.confidence}`;
        messageWrapper.appendChild(confidence);

        // Toggle sources
        const toggle = document.createElement("div");
        toggle.classList.add("toggle-sources");
        toggle.innerText = `▸ View Sources (${metadata.sources.length})`;

        const sourcesContainer = document.createElement("div");
        sourcesContainer.classList.add("sources");
        sourcesContainer.style.display = "none";

        metadata.sources.forEach((source, i) => {
            const sourceItem = document.createElement("div");
            sourceItem.classList.add("source-item");
            sourceItem.innerText =
                `Score: ${metadata.similarity_scores[i].toFixed(2)}\n\n${source}`;
            sourcesContainer.appendChild(sourceItem);
        });

        toggle.onclick = () => {
            const visible = sourcesContainer.style.display === "block";
            sourcesContainer.style.display = visible ? "none" : "block";
            toggle.innerText = visible
                ? `▸ View Sources (${metadata.sources.length})`
                : `▾ Hide Sources`;
        };

        messageWrapper.appendChild(toggle);
        messageWrapper.appendChild(sourcesContainer);
    }

    chatContainer.appendChild(messageWrapper);

    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: "smooth"
    });
}

/* =========================
   Enter to Send
========================= */

document.getElementById("questionInput")
    .addEventListener("keydown", function (e) {
        if (e.key === "Enter") {
            sendMessage();
        }
    });

