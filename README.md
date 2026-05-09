# 💰 FinSense AI
### Multi-Agent Personal Finance Advisor | AMD Developer Hackathon

> Built by **Team Simbiotix** | Powered by **AMD MI300X + Qwen2.5-72B + ROCm**

[![HuggingFace](https://img.shields.io/badge/🤗%20Live%20Demo-HuggingFace-blue)](https://huggingface.co/spaces/Paradox69/finsense-ai)
[![AMD](https://img.shields.io/badge/Compute-AMD%20MI300X-red)](https://www.amd.com/en/developer/resources/cloud-access/amd-developer-cloud.html)
[![CrewAI](https://img.shields.io/badge/Framework-CrewAI-purple)](https://crewai.com)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)

---

## 🎯 The Problem

500+ million working professionals in India make major financial decisions — taking loans, investing, spending — based on gut feeling with no structured guidance. Most have never spoken to a financial advisor in their lives.

**There is no accessible tool that simulates the real consequences of a financial decision before it is made.**

---

## 💡 The Solution

FinSense AI is a **multi-agent decision intelligence system** that gives everyone access to a personal financial advisory team — instantly, for free, in plain language.

Three specialized AI agents collaborate sequentially to analyze any financial decision and deliver a structured, explainable verdict with real wealth projections.

---

## 🤖 How It Works

```
User Input (natural language financial decision)
              ↓
┌─────────────────────────┐
│   Agent 1: Analyst      │
│  - Extracts key figures │
│  - Calculates ratios    │
│  - Identifies patterns  │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│  Agent 2: Risk Evaluator│
│  - Risk score (1-10)    │
│  - Worst case scenario  │
│  - Top risk factors     │
└────────────┬────────────┘
             ↓
┌─────────────────────────┐
│   Agent 3: Advisor      │
│  - GO / WAIT / AVOID    │
│  - Confidence score     │
│  - 3 action steps       │
└────────────┬────────────┘
             ↓
    Structured Output
  Verdict | Risk | Chart | Actions
```

---

## ⚡ Tech Stack

| Layer | Technology |
|---|---|
| **LLM** | Qwen2.5-72B-Instruct |
| **Inference** | vLLM 0.17.1 with ROCm 7.2.0 |
| **Compute** | AMD Instinct MI300X (192GB VRAM) |
| **Cloud** | AMD Developer Cloud |
| **Agent Framework** | CrewAI (sequential pipeline) |
| **Frontend** | Streamlit |
| **Deployment** | HuggingFace Spaces |

---

## 🚀 Live Demo

👉 **[Try FinSense AI on HuggingFace](https://huggingface.co/spaces/Paradox69/finsense-ai)**

**Example queries to try:**
- *"I earn Rs.50,000/month. Should I take a Rs.3L loan at 14% for 2 years?"*
- *"Should I invest Rs.10,000/month in mutual funds or FD?"*
- *"I just got my first job with Rs.35,000 salary. Where should my savings go?"*
- *"Should I buy a Rs.80,000 laptop or save the money?"*

---

## ✨ Features

- **3-Agent Sequential Pipeline** — Analyst → Risk Evaluator → Advisor
- **Transparent Reasoning** — See exactly what each agent was thinking
- **Smart Wealth Projection** — Real compounding math (SIP vs FD vs Loan scenarios)
- **Indian Number Parsing** — Handles Rs.2k, 5L, 2 lakh, 50,000 formats
- **Tabbed UI** — Verdict, Agent Reasoning, Wealth Chart, Action Steps
- **Dark Premium UI** — Professional fintech-grade design
- **Responsible AI** — Disclaimer on every output

---

## 📊 Output Structure

Every analysis returns:

```
✅ VERDICT        → GO / WAIT / AVOID
📊 CONFIDENCE     → 0-100% score with progress bar
⚠️ RISK SCORE     → 1-10 with color coding
💬 WHY            → Agent reasoning in plain language
🎯 ACTION STEPS   → 3 specific, actionable steps
📈 WEALTH CHART   → 1-year and 5-year projection comparison
💡 ALTERNATIVE    → What-if scenario
```

---

## 🛠️ Run Locally

### Prerequisites
- Python 3.10+
- Groq API key (free) — [console.groq.com](https://console.groq.com)

### Setup

```bash
# Clone the repo
git clone https://github.com/akash-xai/finsense-ai
cd finsense-ai

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Create .env file
echo "GROQ_API_KEY=your_groq_key_here" > .env
```

### Configure LLM

**For local development (Groq — free):**

```python
# config/llm.py
def get_llm():
    return "groq/llama-3.3-70b-versatile"
```

**For AMD Developer Cloud (production):**

```python
# config/llm.py
from crewai import LLM
import os

def get_llm():
    return LLM(
        model="openai/Qwen/Qwen2.5-72B-Instruct",
        base_url=os.getenv("AMD_BASE_URL"),
        api_key=os.getenv("AMD_API_KEY", "dummy")
    )
```

### Run

```bash
streamlit run app.py
```

Open **http://localhost:8501** 🎉

---

## 🏗️ Project Structure

```
finsense-ai/
│
├── app.py                  ← Streamlit UI (main entry point)
├── requirements.txt
├── Dockerfile              ← HuggingFace deployment
├── .env                    ← API keys (never commit!)
├── .gitignore
│
├── config/
│   └── llm.py              ← LLM configuration (swap here)
│
├── agents/
│   ├── analyst.py          ← Agent 1: Financial Analyst
│   ├── risk_evaluator.py   ← Agent 2: Risk Evaluator
│   └── advisor.py          ← Agent 3: Financial Advisor
│
├── tasks/
│   └── finance_tasks.py    ← Task definitions for each agent
│
└── crew/
    └── finance_crew.py     ← CrewAI pipeline assembler
```

---

## ☁️ AMD Developer Cloud Setup

```bash
# SSH into AMD droplet
ssh root@YOUR_DROPLET_IP

# Enter Docker container
docker restart rocm
docker exec -it rocm /bin/bash

# Start vLLM server with Qwen2.5-72B
vllm serve Qwen/Qwen2.5-72B-Instruct \
  --host 0.0.0.0 \
  --port 8000 \
  --max-model-len 4096 \
  --gpu-memory-utilization 0.85

# Open firewall port
ufw allow 8000
```

Add to `.env`:
```
AMD_BASE_URL=http://YOUR_DROPLET_IP:8000/v1
AMD_API_KEY=dummy
```

---

## 🌍 Deploy to HuggingFace Spaces

```bash
# Add HuggingFace remote
git remote add space https://huggingface.co/spaces/YOUR_USERNAME/finsense-ai

# Push to HuggingFace
git push space main
```

Add secrets in HuggingFace Space Settings:
```
AMD_BASE_URL = http://YOUR_DROPLET_IP:8000/v1
AMD_API_KEY  = dummy
GROQ_API_KEY = your_groq_key
```

---

## 🎯 Use Cases

| Decision Type | Example Query |
|---|---|
| Loan evaluation | *"Should I take a Rs.3L loan at 14% for 2 years?"* |
| Investment choice | *"Mutual funds or FD for Rs.10,000/month?"* |
| Budget analysis | *"I spend Rs.35,000 on Rs.50,000 salary. Am I overspending?"* |
| Big purchase | *"Should I buy an Rs.80,000 laptop now?"* |
| First job savings | *"Just got my first job. Where should my savings go?"* |

---

## 👥 Team Simbiotix

Built with ❤️ in 72 hours for the **AMD Developer Hackathon** on lablab.ai

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## ⚠️ Disclaimer

FinSense AI is an AI-powered tool for informational purposes only. It does not constitute financial advice. Always consult a certified financial advisor before making major financial decisions.
