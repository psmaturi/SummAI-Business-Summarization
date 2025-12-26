from flask import Flask, render_template, request
from summarizer import summarize_text
import os
import re

# Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
STATIC_DIR = os.path.join(BASE_DIR, "static")

print("BASE_DIR:", BASE_DIR)
print("TEMPLATE_DIR:", TEMPLATE_DIR)
print("STATIC_DIR:", STATIC_DIR)

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)


@app.route('/', methods=['GET', 'POST'])
def index():
    print("🔵 Route started")

    summary = ""
    input_text = ""
    summary_sentences = []
    selected_mode = "extractive"   # default
    selected_length = "medium"     # default

    if request.method == 'POST':
        print("🟡 POST request received")

        # Mode & length from form
        selected_mode = request.form.get("summarize_mode", "extractive")
        selected_length = request.form.get("summary_length", "medium")
        print(f"Mode: {selected_mode}, Length: {selected_length}")

        uploaded_file = request.files.get("uploaded_file")

        # ---------------- FILE UPLOAD ----------------
        if uploaded_file and uploaded_file.filename != "":
            print("🟠 File upload selected")
            file_ext = uploaded_file.filename.lower().split(".")[-1]

            if file_ext == "txt":
                text = uploaded_file.read().decode("utf-8", errors="ignore")

            elif file_ext == "pdf":
                try:
                    import PyPDF2
                    pdf_reader = PyPDF2.PdfReader(uploaded_file)
                    text = ""
                    for page in pdf_reader.pages:
                        text += page.extract_text() or ""
                except Exception as e:
                    print("PDF error:", e)
                    text = "Error reading PDF file."

            else:
                text = "Unsupported file format."

            input_text = text
            summary = summarize_text(text, mode=selected_mode, length=selected_length)

        # --------------- CUSTOM TEXT -----------------
        elif request.form.get("custom_text", "").strip():
            print("🟣 Custom text selected")
            input_text = request.form.get("custom_text", "")
            summary = summarize_text(input_text, mode=selected_mode, length=selected_length)

    # Split summary for highlighting in the UI
    if summary:
        summary_sentences = re.split(r'(?<=[.!?])\s+', summary.strip())
        summary_sentences = [s for s in summary_sentences if s.strip()]

    print("🔴 Returning template…")

    return render_template(
        "index.html",
        summary=summary,
        summary_sentences=summary_sentences,
        input_text=input_text,
        selected_mode=selected_mode,
        selected_length=selected_length,
    )


if __name__ == "__main__":
    print("🚀 Flask is starting...")
    app.run(debug=True)
