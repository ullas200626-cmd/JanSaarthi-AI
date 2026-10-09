
const chatForm = document.getElementById("chat-form");
const messageInput = document.getElementById("message-input");
const chatMessages = document.getElementById("chat-messages");
const sendButton = document.getElementById("send-button");

function addMessage(text, sender) {
    const element = document.createElement("div");
    element.classList.add("message");
    element.classList.add(
        sender === "user" ? "user-message" : "assistant-message"
    );
    element.textContent = text;
    chatMessages.appendChild(element);
    chatMessages.scrollTop = chatMessages.scrollHeight;
    return element;
}

function addControlButton(label, onClick) {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = label;
    button.style.cssText =
        "margin:6px 6px 6px 0;padding:10px 14px;" +
        "border:0;border-radius:8px;cursor:pointer;" +
        "background:#1769aa;color:white;font-size:14px;";
    button.addEventListener("click", onClick);
    return button;
}

function addTrackingForm() {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message", "assistant-message");

    const heading = document.createElement("p");
    heading.textContent = "Track a demo complaint";
    wrapper.appendChild(heading);

    const form = document.createElement("form");
    const input = document.createElement("input");
    input.type = "text";
    input.placeholder = "Enter complaint ID (e.g. JS-AB12CD34)";
    input.required = true;
    input.maxLength = 20;
    input.style.cssText =
        "padding:10px;width:100%;max-width:280px;" +
        "box-sizing:border-box;border:1px solid #aaa;border-radius:6px;";

    const trackButton = document.createElement("button");
    trackButton.type = "submit";
    trackButton.textContent = "Track";
    trackButton.style.cssText =
        "margin:6px;padding:10px 14px;border:0;" +
        "border-radius:8px;cursor:pointer;background:#1769aa;color:white;";

    form.append(input, trackButton);
    wrapper.appendChild(form);
    chatMessages.appendChild(wrapper);

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        const id = input.value.trim().toUpperCase();
        trackButton.disabled = true;

        try {
            const response = await fetch(
                `/api/complaints/${encodeURIComponent(id)}`
            );
            const result = await response.json();

            if (!response.ok) {
                addMessage(result.error || "Could not find that complaint.", "assistant");
                return;
            }

            const c = result.complaint;
            addMessage(
                `DEMO COMPLAINT STATUS\nID: ${c.complaint_id}\n` +
                `Issue: ${c.issue}\nStatus: ${c.status}\n` +
                `Created: ${c.created_at}\n\n${result.notice}`,
                "assistant"
            );
        } catch (error) {
            console.error("Tracking failed:", error);
            addMessage("Unable to reach the server. Please try again.", "assistant");
        } finally {
            trackButton.disabled = false;
        }
    });

    chatMessages.scrollTop = chatMessages.scrollHeight;
}

function addRegistrationButton(issue, message, language) {
    const wrapper = document.createElement("div");
    wrapper.classList.add("message", "assistant-message");

    const note = document.createElement("p");
    note.textContent =
        "Want to save this as a demo complaint and receive a tracking ID?";
    wrapper.appendChild(note);

    const button = addControlButton("Register demo complaint", async () => {
        button.disabled = true;
        button.textContent = "Registering...";

        try {
            const response = await fetch("/api/complaints", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ message, issue, language })
            });

            const result = await response.json();

            if (!response.ok) {
                addMessage(result.error || "Registration failed.", "assistant");
                button.disabled = false;
                button.textContent = "Try registration again";
                return;
            }

            const c = result.complaint;
            addMessage(
                `Demo complaint saved successfully!\n` +
                `Complaint ID: ${c.complaint_id}\n` +
                `Issue: ${c.issue}\nStatus: ${c.status}\n` +
                `Created: ${c.created_at}\n\n` +
                `${result.notice}\nKeep this ID to track your demo record.`,
                "assistant"
            );

            button.textContent = "Complaint registered";
            addTrackingForm();
        } catch (error) {
            console.error("Registration failed:", error);
            addMessage("Unable to reach the server. Please try again.", "assistant");
            button.disabled = false;
            button.textContent = "Try registration again";
        }
    });

    wrapper.appendChild(button);
    chatMessages.appendChild(wrapper);
    chatMessages.scrollTop = chatMessages.scrollHeight;
}

chatForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const message = messageInput.value.trim();
    if (!message || sendButton.disabled) return;

    addMessage(message, "user");
    messageInput.value = "";
    sendButton.disabled = true;
    sendButton.textContent = "Sending...";

    const loadingMessage = addMessage("Please wait...", "assistant");

    try {
        const response = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        const result = await response.json();
        loadingMessage.remove();

        if (!response.ok || typeof result.reply !== "string") {
            addMessage(result.error || "Sorry, something went wrong.", "assistant");
            return;
        }

        addMessage(result.reply, "assistant");

        if (result.issue) {
            addRegistrationButton(result.issue, message, result.language);
        }
    } catch (error) {
        loadingMessage.remove();
        console.error("Chat request failed:", error);
        addMessage(
            "Unable to connect to the server. Check that JanSaarthi AI is running.",
            "assistant"
        );
    } finally {
        sendButton.disabled = false;
        sendButton.textContent = "Send ↗";
        messageInput.focus();
    }
});