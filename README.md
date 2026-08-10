---
title: Shopify Store Chatbot
emoji: 🛍️
colorFrom: blue
colorTo: purple
sdk: gradio
sdk_version: 6.22.0
app_file: main.py
pinned: false
---

# Shopify Store FAQ Chatbot

**Live URL:** https://shopify-chatbot-wmgr.onrender.com

> Note: Hosted on Render free tier — first load after inactivity may take ~30 seconds to wake up.

---

## What it does

An AI-powered customer support chatbot for Shopify stores. Customers can ask questions by **typing or recording their voice** and the bot answers based only on the store information you provide.

---

## Tech Stack

| Layer | Technology | Role |
|---|---|---|
| **UI Framework** | [Gradio](https://gradio.app) by HuggingFace | Web interface — chat, voice input, examples |
| **LLM** | Llama 3.3 70B (via [Groq](https://groq.com)) | Reads store context and generates answers |
| **Speech-to-Text** | Whisper Large V3 Turbo (via [Groq](https://groq.com)) | Converts voice recordings to text questions |
| **LLM Client** | [LiteLLM](https://litellm.ai) | Unified interface to call Groq's LLM API |
| **Hosting** | [Render.com](https://render.com) | Free cloud hosting for the Python web server |

---

## How it works

```
Customer types or speaks a question
        │
        ▼
[Groq Whisper]  ←  voice input only
        │
        ▼
Question text  +  Store context (products, policies, FAQs)
        │
        ▼
[Groq Llama 3.3]  →  Answer grounded only in store info
        │
        ▼
Chat response displayed in Gradio UI
```

This approach is called **RAG-lite** (Retrieval Augmented Generation) — the LLM doesn't make things up, it only answers from the context you provide.

---

## Run locally

```bash
# 1. Clone the repo
git clone https://github.com/manojkm/shopify-chatbot
cd shopify-chatbot

# 2. Create .env file
echo "GROQ_API_KEY=your_key_here" > .env

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run
python main.py
```

Open http://127.0.0.1:7860 in your browser.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Get a free key at console.groq.com |
| `SHOPIFY_STORE` | Optional | e.g. `mystore.myshopify.com` (for live data) |
| `SHOPIFY_ACCESS_TOKEN` | Optional | Admin API token (`shpat_...`) for live data |
