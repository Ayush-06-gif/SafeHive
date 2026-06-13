# 🛡️ SAFEhive

An AI-powered security sandbox for analyzing suspicious files, URLs, and code in an isolated environment. SAFEhive helps users detect malware, phishing attempts, and malicious behavior using multiple AI agents and automated security analysis.

## 🚀 Features

* Multi-agent AI architecture
* File analysis and malware detection
* URL reputation and phishing analysis
* Static code analysis
* AI-generated security reports
* Risk scoring system
* Explainable threat assessment
* Support for multiple LLM providers
* Fallback model support
* Modern web interface
* Real-time analysis pipeline

---

## 🏗️ Architecture

```text
                    User
                      │
                      ▼
               Frontend (Next.js)
                      │
                      ▼
                API Gateway
                      │
      ┌───────────────┴───────────────┐
      ▼                               ▼
 Agent Orchestrator             Report Generator
      │
      ├──────── File Analysis Agent
      ├──────── URL Analysis Agent
      ├──────── Code Analysis Agent
      ├──────── Threat Intelligence Agent
      └──────── Risk Scoring Agent
                      │
                      ▼
                 LLM Layer
          ┌─────────────────────┐
          │ Groq (Primary LLM)  │
          │ Gemini Flash Backup │
          └─────────────────────┘
```

---

## 🛠️ Tech Stack

### Frontend

* Next.js
* TypeScript
* Tailwind CSS
* ShadCN UI

### Backend

* FastAPI
* Python
* LangGraph
* LangChain

### AI Models

* Groq (Llama 3.1 8B Instant)
* Gemini Flash (Backup)

### Database

* PostgreSQL
* Redis

### Deployment

* Docker
* Vercel
* Railway

---

## 📂 Project Structure

```text
SAFEhive/
│
├── frontend/
├── backend/
├── agents/
│   ├── file_agent/
│   ├── url_agent/
│   ├── code_agent/
│   ├── threat_agent/
│   └── scoring_agent/
│
├── reports/
├── database/
├── docs/
├── tests/
├── docker/
└── README.md
```

---

## ⚡ Installation

Clone the repository:

```bash
git clone https://github.com/yourusername/SAFEhive.git
cd SAFEhive
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run the backend:

```bash
uvicorn app:app --reload
```

Run the frontend:

```bash
npm install
npm run dev
```

---

## 🔍 Workflow

1. Upload a file, URL, or code snippet.
2. SAFEhive routes the request to specialized AI agents.
3. Agents perform security analysis.
4. Risk scores are calculated.
5. A detailed report is generated.
6. Results are displayed through the dashboard.

---

## 📊 Example Output

```json
{
  "threat_level": "High",
  "risk_score": 89,
  "malicious_indicators": [
    "Suspicious network activity",
    "Encoded PowerShell commands",
    "Potential phishing domain"
  ],
  "recommendation": "Block and quarantine immediately"
}
```

---

## 🎯 Future Improvements

* Dynamic sandbox execution
* VirusTotal integration
* YARA rule engine
* PDF and document analysis
* Browser extension
* Real-time monitoring
* SIEM integration
* Kubernetes deployment
* Multi-user dashboard
* Alerting system

---

## 🤝 Contributing

Contributions are welcome. Feel free to open issues and submit pull requests.

---

## 📜 License

This project is licensed under the MIT License.

---

## ⭐ Support

If you find this project useful, consider giving it a star on GitHub.

---

Built with ❤️ using AI and modern security technologies.
