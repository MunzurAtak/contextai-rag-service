const API_URL = "http://127.0.0.1:8000";

/* =========================
   File Selection Feedback
========================= */

document.getElementById("fileInput").addEventListener("change", function () {
    const label = document.getElementById("uploadFileName");
    const area = document.getElementById("uploadLabel");

    if (this.files.length) {
        label.textContent = this.files[0].name;
        area.classList.add("has-file");
    } else {
        label.textContent = "Click to select a PDF";
        area.classList.remove("has-file");
    }
});

/* =========================
   Upload Document
========================= */

async function uploadFile() {
    const fileInput = document.getElementById("fileInput");
    const status = document.getElementById("uploadStatus");

    if (!fileInput.files.length) return;

    status.textContent = "Indexing…";
    status.className = "";

    const formData = new FormData();
    formData.append("file", fileInput.files[0]);

    try {
        const response = await fetch(`${API_URL}/upload`, {
            method: "POST",
            body: formData
        });

        if (!response.ok) throw new Error("Upload failed");

        const data = await response.json();
        status.textContent = `✓ ${data.num_chunks} chunks indexed`;
        status.className = "success";

        document.getElementById("docName").textContent =
            `${fileInput.files[0].name}`;
    } catch {
        status.textContent = "Upload failed. Is the server running?";
        status.className = "error";
    }
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

    // Hide empty state on first message
    const emptyState = document.getElementById("emptyState");
    if (emptyState) emptyState.remove();

    addMessage(question, "user");
    input.value = "";

    // Typing indicator
    const thinkingWrapper = document.createElement("div");
    thinkingWrapper.classList.add("message-wrapper", "bot");

    const thinking = document.createElement("div");
    thinking.classList.add("message", "bot", "typing");
    thinking.innerHTML = "<span></span><span></span><span></span>";

    thinkingWrapper.appendChild(thinking);
    chatContainer.appendChild(thinkingWrapper);
    scrollToBottom(chatContainer);

    try {
        const response = await fetch(`${API_URL}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question, top_k: parseInt(topK) })
        });

        if (!response.ok) throw new Error("Request failed");

        const data = await response.json();
        chatContainer.removeChild(thinkingWrapper);
        addMessage(data.answer, "bot", data);
    } catch {
        chatContainer.removeChild(thinkingWrapper);
        addMessage("Something went wrong. Please check the server.", "bot");
    }
}

/* =========================
   Add Message to UI
========================= */

function addMessage(text, type, metadata = null) {
    const chatContainer = document.getElementById("chatContainer");

    const wrapper = document.createElement("div");
    wrapper.classList.add("message-wrapper", type);

    const message = document.createElement("div");
    message.classList.add("message", type);
    message.textContent = text;
    wrapper.appendChild(message);

    if (metadata && type === "bot") {
        // Confidence badge
        const level = metadata.confidence.toLowerCase();
        const badge = document.createElement("div");
        badge.classList.add("confidence-badge", level);
        badge.textContent = `${metadata.confidence} confidence`;
        wrapper.appendChild(badge);

        // Toggle sources
        if (metadata.sources && metadata.sources.length) {
            const toggle = document.createElement("div");
            toggle.classList.add("toggle-sources");
            toggle.innerHTML = `
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"
                    fill="none" stroke="currentColor" stroke-width="2.5">
                    <polyline points="9 18 15 12 9 6"></polyline>
                </svg>
                View Sources (${metadata.sources.length})
            `;

            const sourcesContainer = document.createElement("div");
            sourcesContainer.classList.add("sources");
            sourcesContainer.style.display = "none";

            metadata.sources.forEach((source, i) => {
                const score = metadata.similarity_scores[i];
                const item = document.createElement("div");
                item.classList.add("source-item");

                const bar = document.createElement("div");
                bar.classList.add("source-score-bar");
                bar.innerHTML = `
                    <span class="score-label">Score ${score.toFixed(2)}</span>
                    <div class="score-track">
                        <div class="score-fill" style="width: ${Math.round(score * 100)}%"></div>
                    </div>
                `;

                const content = document.createElement("div");
                content.classList.add("source-text");
                content.textContent = source;

                item.appendChild(bar);
                item.appendChild(content);
                sourcesContainer.appendChild(item);
            });

            let open = false;
            toggle.onclick = () => {
                open = !open;
                sourcesContainer.style.display = open ? "flex" : "none";
                toggle.innerHTML = open
                    ? `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"
                            fill="none" stroke="currentColor" stroke-width="2.5">
                            <polyline points="6 9 12 15 18 9"></polyline>
                        </svg> Hide Sources`
                    : `<svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24"
                            fill="none" stroke="currentColor" stroke-width="2.5">
                            <polyline points="9 18 15 12 9 6"></polyline>
                        </svg> View Sources (${metadata.sources.length})`;
            };

            wrapper.appendChild(toggle);
            wrapper.appendChild(sourcesContainer);
        }
    }

    chatContainer.appendChild(wrapper);
    scrollToBottom(chatContainer);
}

/* =========================
   Helpers
========================= */

function scrollToBottom(el) {
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
}

document.getElementById("questionInput").addEventListener("keydown", (e) => {
    if (e.key === "Enter") sendMessage();
});
