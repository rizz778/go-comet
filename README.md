# Multi-Agent Trade Document Compliance Platform

An end-to-end intelligent audit portal designed to extract, validate, and route shipment trade documentation (such as Bills of Lading, Invoices, and Packing Lists). The platform automates checks against custom customer compliance rule sets, logs execution logs in a local SQLite database, allows manual operator-in-the-loop review overrides, and supports natural language database querying.

---

## 🚀 Key Features

1. **Multi-Agent Verification Pipeline (LangGraph)**
   * **Extractor Agent:** Utilizes **Gemini 2.5 Flash** (inline byte payloads) to extract structured parameters (consignee, HS code, weight, ports, incoterms) from PDFs/images with confidence scores.
   * **Validator Agent:** A 100% deterministic validator matching extracted data against a customer-specific `rules.json` rule set (supports exact, prefix, allow list, regex patterns, and numeric checks).
   * **Router Agent:** Classifies shipments into lanes (`auto_approve`, `flag_review`, or `amendment_request`) and invokes **Mistral AI** to generate reasoning summaries and email drafts.
2. **Local SQLite Audit Storage & Analytics**
   * Stores runs history including original extraction data, validation rule logs, final decisions, and operator overrides.
   * Exposes backend endpoints for tabular registry browsing and analytics totals.
3. **Operator-in-the-Loop Review Console**
   * High-fidelity dark-mode UI highlighting compliance warnings and extraction confidence.
   * Allows manual overrides of OCR values and interactive editing of drafted supplier amendment notifications.
4. **Natural Language Database Query Assistant**
   * Translates plain English operational questions (e.g. *"Show me filenames of all flagged runs"*) into SQL queries, executes them against SQLite, and summarizes findings.

---

## 🛠️ Technology Stack

* **Backend:** Python 3.10+, FastAPI, LangGraph, LangChain, SQLite, Uvicorn.
* **Frontend:** React, Vite, TypeScript, Tailwind CSS v4, Lucide Icons.

---

## 📂 Project Structure

```
go-comet/assignment/
├── backend/                  # FastAPI Application
│   ├── agents/               # Extractor, Validator, and Router agents
│   ├── config/               # Settings, LLM providers, and rules.json
│   ├── controllers/          # Modular API request handlers
│   ├── graph/                # LangGraph state machine workflow
│   ├── routes/               # API endpoint routing
│   ├── services/             # SQLite storage and NL SQL query translation
│   ├── sample_docs/          # Test PDF invoices
│   └── app.py                # App entrypoint
├── client/                   # React Application
│   ├── src/
│   │   ├── api/              # Modular API fetch handlers (baseApi, uploadApi, etc.)
│   │   ├── components/       # SideBar, AnalyticsCards, ReviewPanel, etc.
│   │   ├── pages/            # Tab views (AuditDesk, HistoryRegistry, NLQueryAssistant)
│   │   ├── types/            # TypeScript interfaces
│   │   ├── App.tsx           # Application shell
│   │   └── main.tsx          # React main entry
│   └── vite.config.ts        # Vite configuration (port 3000 & port 8000 proxy)
└── README.md                 # Project README
```

---

## ⚙️ Environment Configuration

Create a file named `.env` in the `backend/` directory:

```env
GEMINI_API_KEY=your_gemini_api_key
GEMINI_MODEL=gemini-2.5-flash

MISTRAL_API_KEY=your_mistral_api_key
MISTRAL_MODEL=mistral-small-latest

DEFAULT_LLM_PROVIDER=mistral
```

---

## 🏃 Getting Started

### 1. Run the Backend Server
From the project root:

```powershell
cd backend
# Activate virtual environment
.\venv\Scripts\activate
# Start Uvicorn
uvicorn app:app --reload
```
* The backend will run on `http://127.0.0.1:8000/`.

### 2. Run the Frontend Client
From the project root:

```powershell
cd client
# Install packages
npm install
# Start Vite development server
npm run dev
```
* Open your browser and navigate to `http://localhost:3000/` to use the dashboard!

---

## 🧪 Testing the Pipeline via cURL

You can bypass the UI and test the upload endpoint directly using a terminal window:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/pipeline/upload" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "file=@backend/sample_docs/clean_invoice.pdf"
```
