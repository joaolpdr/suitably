# 📚 Suitably

> An educational financial assistant that explains investment products **according to the user's suitability profile**, built for beginners who have never invested.

**🔗 Try it live:** [suitably-edu.streamlit.app](https://suitably-edu.streamlit.app)

Suitably combines a **rule-based suitability engine** (written and tested in Python) with an **LLM tutor** (Gemini). The rules decide what fits the user; the AI only explains. It never recommends.

Built as the final project of the DIO *"Create Your Smart Chatbot for the Financial Market"* challenge, then extended with compliance-oriented design decisions.

---

## ✨ Features

- **Suitability questionnaire**: 4 questions that classify the user as *Conservative*, *Moderate* or *Aggressive*
- **Knockout rules**: no emergency fund or a horizon under 1 year caps the profile at *Conservative*, regardless of the score
- **Product classification**: the catalog is split into *suitable* and *not suitable* for the profile
- **Edu, the AI tutor**: explains products in plain language, from everyday analogy to technical term
- **Voice conversation**: ask by voice and Edu answers with text **and** audio
- **Graceful error handling**: API outages show a friendly message instead of breaking the app

## 🧠 Design decisions

| Decision | Why |
|---|---|
| **Rules in Python, explanations by the LLM** | An LLM must never decide suitability. The profile and the product classification are computed deterministically and passed to the model as fixed context |
| **Knockout rules on top of the score** | A pure sum lets risk appetite "compensate" for lack of liquidity. Real suitability questionnaires use eliminatory criteria |
| **No pre-selected answers** (`index=None`) | A default option can bias the profile when users click through without reading |
| **No tax information** | Tax rules change often. Edu is explicitly forbidden from stating tax rules and points to official sources instead |
| **Beginner-first, progressive terminology** | Edu starts with analogies and introduces the technical name afterwards (*idea → analogy → term*), so users actually learn the vocabulary |
| **Disclaimer on the first product answer only** | Repeating it in every message creates banner blindness. It stays fixed at the top of the page |
| **Voice replies only for voice questions** | Audio adds 2 extra API calls; text users don't pay that cost |

## 🏗️ Architecture

```
app.py          → Streamlit interface: questionnaire, results, chat, voice
suitability.py  → business rules: questions, scoring, knockout rules, product filter
agent.py        → Gemini integration: Edu's instructions and chat creation
voz.py          → voice: speech-to-text and text-to-speech
data/produtos.json  → product catalog
tests/          → unit tests for the suitability rules
```

Business rules, AI and interface are separated: changing the LLM only touches `agent.py`; changing the scoring only touches `suitability.py`.

## 🚀 Getting started

**Requirements:** Python 3.10+ and a [Gemini API key](https://aistudio.google.com/apikey).

```bash
git clone https://github.com/joaolpdr/suitably.git
cd suitably
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env        # then add your API key to .env
streamlit run app.py
```

Run the tests:

```bash
pytest -v
```

## 🛠️ Tech stack

Python · Streamlit · Google Gemini (text, speech-to-text and TTS) · pytest

## ⚠️ Known limitations

- **Simplified questionnaire**: real suitability assessments also consider assets, experience and financial knowledge
- **Risk-only classification**: products are filtered by risk, not by liquidity. A product locked until maturity can still be "suitable" for a short horizon
- **LLM terminology**: the model may occasionally use an imprecise financial term
- **Response time**: voice answers chain 3 API calls and can take several seconds
- **Privacy**: voice recordings are sent to Google (Gemini) for processing. The interface informs the user

## 🗺️ Roadmap

- [ ] Show which knockout rule limited the profile, on screen and to Edu
- [ ] Add a liquidity × horizon criterion to product suitability
- [ ] Shorter spoken answers and streaming text to reduce perceived latency
- [ ] Personal glossary of terms the user has learned during the conversation
- [ ] Deploy on Streamlit Community Cloud

---

> **Disclaimer:** Suitably is an educational project. It does not provide investment advice.