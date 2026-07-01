const form = document.getElementById("shorten-form");
const input = document.getElementById("url-input");
const result = document.getElementById("result");
const error = document.getElementById("error");
const shortUrl = document.getElementById("short-url");
const copyButton = document.getElementById("copy-button");
const contactForm = document.getElementById("contact-form");
const contactStatus = document.getElementById("contact-status");
const shortenerPanel = document.querySelector(".shortener-panel");

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    result.style.display = "none";
    error.style.display = "none";
    shortUrl.value = "";

    try {
        const response = await fetch("/shorten", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify({
                original_url: input.value,
            }),
        });

        if (!response.ok) {
            throw new Error("Please enter a valid URL.");
        }

        const data = await response.json();
        shortUrl.value = data.short_url;
        result.style.display = "block";
    } catch (err) {
        error.textContent = err.message;
        error.style.display = "block";
    }
});

copyButton.addEventListener("click", async () => {
    await navigator.clipboard.writeText(shortUrl.value);
    copyButton.textContent = "Copied";

    setTimeout(() => {
        copyButton.textContent = "Copy";
    }, 1200);
});

contactForm.addEventListener("submit", (event) => {
    event.preventDefault();
    contactStatus.style.display = "block";
    contactForm.reset();
});

shortenerPanel.addEventListener("mousemove", (event) => {
    const panelRect = shortenerPanel.getBoundingClientRect();
    const x = event.clientX - panelRect.left;
    const y = event.clientY - panelRect.top;
    const rotateY = ((x / panelRect.width) - 0.5) * 12;
    const rotateX = -((y / panelRect.height) - 0.5) * 10;

    shortenerPanel.style.setProperty("--tilt-x", `${rotateX.toFixed(2)}deg`);
    shortenerPanel.style.setProperty("--tilt-y", `${rotateY.toFixed(2)}deg`);
});

shortenerPanel.addEventListener("mouseleave", () => {
    shortenerPanel.style.setProperty("--tilt-x", "4deg");
    shortenerPanel.style.setProperty("--tilt-y", "-6deg");
});
