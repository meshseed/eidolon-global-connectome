# 🏠 Local LLM (Private Mode) Setup Guide

Eidolon Mesh v3.5 supports running completely offline using your own local hardware. This privacy-focused mode keeps all your data on your machine and generates knowledge using open-source models (via Ollama).

## 🚀 Prerequisites

1.  **Ollama**: Download and install from [ollama.com](https://ollama.com).
2.  **Models**: Open your terminal and run:
    ```bash
    ollama pull gemma:2b
    ollama pull nomic-embed-text
    ```
    *(Note: We recommend `gemma:2b` for speed on most laptops, but you can use `llama3`, `mistral`, or any other model your hardware supports.)*

---

## 🛠️ Configuration (One-Time Setup)

Because web browsers are secure environments, they block the public website (`https://eidolon-mesh.net`) from talking to your private local computer (`http://localhost`) by default. You need to unlock this bridge once.

### Step 1: Allow Browser Access (CORS)

By default, Ollama only listens to itself. You must tell it to listen to web browsers.

**For Windows:**
1.  **Quit Ollama** (Right-click the icon in the System Tray -> Quit).
2.  Open **PowerShell** and run:
    ```powershell
    setx OLLAMA_ORIGINS "*"
    ```
3.  **Restart Ollama** from the Start Menu.

**For Mac/Linux:**
1.  Run `launchctl setenv OLLAMA_ORIGINS "*"` (Mac) or add it to your service config.
2.  Restart the Ollama application.

### Step 2: Unlock Browser Security

Modern browsers block "Mixed Content" (HTTP resources on an HTTPS site).

1.  Open [https://eidolon-mesh.net](https://eidolon-mesh.net).
2.  Click the **Lock Icon 🔒** (to the left of the URL).
3.  Click **Site Settings**.
4.  Scroll down to **Insecure content**.
5.  Change it from **Block** to **Allow**.
6.  **Refresh** the Eidolon Mesh page.

*(Note: This only allows the site to talk to your localhost. It does not make the site "unsafe" for general browsing.)*

---

## 🔌 Connecting via Settings

1.  Open **Settings** (🧬 Icon) in the PWA.
2.  Change **LLM Provider** to `🏠 Local LLM (Self-hosted)`.
3.  Ensure the settings match your setup:
    -   **Endpoint:** `http://localhost:11434`
    -   **Text Model:** `gemma:2b`
    -   **Embedding Model:** `nomic-embed-text`
4.  Click **🔌 Test Connection**.
    -   You should see: **"✅ Connection Successful!"**

## 🧬 Final Step: Regenerate Knowledge

Your "Cloud" knowledge (Gemini embeddings) is incompatible with your "Local" knowledge (Ollama embeddings).

1.  Go to **Settings > Advanced**.
2.  Click **🧬 Regenerate Missing Embeddings**.
3.  Wait for the process to finish (the progress bar will show on custom elements).

**You are now fully offline and private! 🛡️**
