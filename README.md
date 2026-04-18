# Jarvis: Screen Insight Agent ⚡

Jarvis is a high-performance, proactive AI assistant designed to provide real-time screen analysis and actionable insights. Built with a sleek, glassmorphic interface and powered by the cutting-edge **Groq Llama 4 Scout** vision engine, Jarvis doesn't just see your screen—he understands your intent.

![Jarvis Concept](https://img.shields.io/badge/AI-Jarvis-blue?style=for-the-badge)
![Groq](https://img.shields.io/badge/Powered%20By-Groq-orange?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/Backend-FastAPI-green?style=for-the-badge)

## 🚀 Features

- **Multimodal Intelligence**: Uses Groq's Llama 4 Scout to analyze complex UI layouts, file structures, and active workflows.
- **Proactive Persona**: Jarvis speaks with a professional, authoritative, and concise tone (inspired by Iron Man's JARVIS).
- **Glassmorphic UI**: A premium, responsive web dashboard for real-time summaries and chat interactions.
- **Agentic Decision Support**: Provides non-obvious "Key Information" and proactive "Action Items" rather than just OCR text.
- **Privacy First**: Local screen capture and processing with secure environment configuration.

## 🛠️ Tech Stack

- **Backend**: FastAPI (Python)
- **Vision Engine**: Groq (Llama 4 Scout 17B)
- **Frontend**: HTML5, Vanilla JS, CSS (Modern Glassmorphism)
- **Capture**: Custom Python screen-tool module

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/r1shabhgarg/jarvis-vision.git
   cd jarvis-vision
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure Environment:**
   Create a `.env` file in the root directory:
   ```env
   GROQ_API_KEY=your_groq_api_key_here
   ```

## 🚦 Usage

1. **Start the Jarvis Backend:**
   ```bash
   python app.py
   ```
2. **Access the Dashboard:**
   Open `http://localhost:8080` in your browser.
3. **Analyze:**
   Click the capture button to let Jarvis analyze your workspace.

## 🛡️ Security

Your API keys are protected. The repository includes a `.gitignore` that prevents `.env` and local `.uploads` from being pushed to GitHub.

---
*Built for the future of agentic computing.*
