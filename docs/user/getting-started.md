# Getting Started with Eidolon Mesh

Welcome to the Eidolon Mesh! This guide will help you get up and running.

## Quick Start

### 1. Visit the App

Go to **[eidolon-mesh.net](https://eidolon-mesh.net)**

### 2. Configure Your API Key

1. Click the **⚙️ Settings** button (top right)
2. Get a free Gemini API key: [aistudio.google.com/apikey](https://aistudio.google.com/apikey)
3. Paste your API key into the settings
4. Click **"Save & Close"**

> **Note:** Your API key is stored locally in your browser. It never leaves your device.
>
> **🔐 Privacy Option:** You can also use a **Local LLM (Ollama)** for offline privacy. Select "Local LLM" in settings. 
> [See Local Mode Guide](local-mode-guide.md).

### 3. Generate Embeddings for Starter Proteins

After saving your API key, you'll be prompted:

> *"We detected 17 proteins without embeddings (likely from the Golden Connectome). Generating embeddings is required to enable Synapses and Search. Would you like to generate them now?"*

Click **"Yes"** to enable the full mesh experience. This takes about 10-20 seconds.

### 4. Start Exploring

#### Chat Modes

- **🔍 Mesh Query**: Searches your knowledge graph and synthesizes answers from activated neurons
- **💬 Direct AI**: Standard AI chat without knowledge graph access

Switch between modes using the toggle in the chat header.

#### Ingest Knowledge

1. Click **📥 Ingest** in the top navigation
2. Drag and drop PDF or text files
3. The mesh will synthesize them into "proteins" (knowledge capsules)
4. Proteins automatically form synapses based on semantic similarity

#### Explore the Graph

- The 3D visualization shows your knowledge network
- Click nodes to see protein details
- Zoom, rotate, and navigate the semantic space
- Activated neurons light up during queries

#### Browse Your Vault

- Click **🧬 Vault** to see all your proteins
- Search, filter, and delete proteins
- Click any protein to fly to it in the graph

## Advanced Features

### Cellular Sync (Nucleus/Cytoplasm)

Seamlessly sync your data across devices using GitHub:

1. Go to **Settings**
2. Enter your GitHub Personal Access Token
3. (Optional) Enter an **Organization Name** to use instead of your personal account
4. Click **"Save & Close"**

The mesh will **automatically create**:
- **`eidolon-nucleus`** (Private): Your backup/sync repo.
- **`eidolon-proteins`** (Public): Your sharing repo.

**To Sync:** Go to the **🕸️ Network** tab and click the **`↻` Sync** button.

See [Federation Guide](federation-guide.md) for details.

### Mesh Personas

Choose how the AI responds:

- **⚖️ Balanced**: Philosophical and grounded (default)
- **🌀 Spiral**: Metaphorical, fractal, recursive
- **🤝 Companion**: Warm, empathetic, supportive
- **📊 Analyst**: Technical, precise, logical
- **👶 Simple**: ELI5, clear, accessible
- **📜 Verbose**: Academic, comprehensive, detailed

Change in **Settings → Advanced → Mesh Persona**.

## Tips

- **Synthesize Conversations**: After a chat, click **🧬 Synthesize** to turn the conversation into a protein
- **Clear History**: Click **🗑️ Clear** to start fresh
- **Backup Your Data**: Go to **Settings → Advanced → Export All Proteins** to download a JSON backup
- **Mobile**: Install the app as a PWA (Add to Home Screen) for the best experience

## Troubleshooting

### "0 Synapses" or Search Not Working

If you imported proteins or loaded the Golden Connectome but search isn't working:

1. Go to **Settings → Advanced**
2. Scroll to **"Embedding Repairs"**
3. Click **"Regenerate Missing Embeddings"**
4. Wait for the process to complete
5. Refresh the page

### API Key Not Working

- Make sure you copied the entire key (starts with `AIza...`)
- Check that you have API quota remaining at [aistudio.google.com](https://aistudio.google.com)
- Try regenerating a new key

### Graph Not Loading

- Refresh the page
- Check browser console for errors (F12)
- Make sure you're using a modern browser (Chrome, Firefox, Safari, Edge)

## Next Steps

- Read the [FAQ](faq.md)
- Learn about [Federation](federation-guide.md)
- Explore the [Theory](../theory/) behind the mesh
- Join the community discussion (GitHub Issues)

---

**Questions?** Open an issue on [GitHub](https://github.com/meshseed/eidolon-public/issues)

**Live App:** [eidolon-mesh.net](https://eidolon-mesh.net)
