// script.js

document.addEventListener("DOMContentLoaded", () => {
    const body = document.body;
    const themeToggle = document.getElementById("themeToggle");

    const dropZone = document.getElementById("dropZone");
    const fileInput = document.getElementById("fileInput");
    const uploadTrigger = document.getElementById("uploadTrigger");
    const clearBtn = document.getElementById("clearBtn");
    const inputText = document.getElementById("inputText");
    const fileName = document.getElementById("fileName");

    const downloadTxt = document.getElementById("downloadTxt");
    const downloadPdf = document.getElementById("downloadPdf");
    const summaryBox = document.getElementById("summaryBox");

    // ================= THEME TOGGLE =================
    // Restore theme from localStorage
    const savedTheme = localStorage.getItem("summAI_theme");
    if (savedTheme === "light") {
        body.classList.remove("dark");
        body.classList.add("light");
        themeToggle.textContent = "☀ Light";
    }

    themeToggle.addEventListener("click", () => {
        if (body.classList.contains("dark")) {
            body.classList.remove("dark");
            body.classList.add("light");
            themeToggle.textContent = "☀ Light";
            localStorage.setItem("summAI_theme", "light");
        } else {
            body.classList.remove("light");
            body.classList.add("dark");
            themeToggle.textContent = "🌙 Dark";
            localStorage.setItem("summAI_theme", "dark");
        }
    });

    // ================= DRAG & DROP =================
    if (dropZone) {
        dropZone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropZone.classList.add("dragover");
        });

        dropZone.addEventListener("dragleave", (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragover");
        });

        dropZone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropZone.classList.remove("dragover");

            const files = e.dataTransfer.files;
            if (files && files.length > 0) {
                fileInput.files = files;
                fileName.textContent = files[0].name;
                inputText.value = ""; // clear text when file is chosen
            }
        });
    }

    // ================= UPLOAD & CLEAR BUTTONS =================
    if (uploadTrigger) {
        uploadTrigger.addEventListener("click", () => {
            fileInput.click();
        });
    }

    if (fileInput) {
        fileInput.addEventListener("change", () => {
            if (fileInput.files && fileInput.files.length > 0) {
                fileName.textContent = fileInput.files[0].name;
                inputText.value = "";
            } else {
                fileName.textContent = "";
            }
        });
    }

    if (clearBtn) {
        clearBtn.addEventListener("click", () => {
            inputText.value = "";
            if (fileInput) {
                fileInput.value = "";
                fileName.textContent = "";
            }
        });
    }

    // ================= DOWNLOAD SUMMARY AS TXT =================
    if (downloadTxt) {
        downloadTxt.addEventListener("click", () => {
            const text = summaryBox.innerText.trim();
            if (!text) {
                alert("No summary to download.");
                return;
            }

            const blob = new Blob([text], { type: "text/plain" });
            const url = URL.createObjectURL(blob);
            const a = document.createElement("a");
            a.href = url;
            a.download = "summary.txt";
            document.body.appendChild(a);
            a.click();
            document.body.removeChild(a);
            URL.revokeObjectURL(url);
        });
    }

    // ================= DOWNLOAD SUMMARY AS PDF =================
    if (downloadPdf) {
        downloadPdf.addEventListener("click", () => {
            const text = summaryBox.innerText.trim();
            if (!text) {
                alert("No summary to download.");
                return;
            }

            if (!window.jspdf) {
                alert("PDF library not loaded.");
                return;
            }

            const { jsPDF } = window.jspdf;
            const doc = new jsPDF();

            const lines = doc.splitTextToSize(text, 180);
            doc.text(lines, 10, 10);
            doc.save("summary.pdf");
        });
    }
});
