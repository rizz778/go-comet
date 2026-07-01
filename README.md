# Multi-Agent Trade Document Compliance Platform

An end-to-end intelligent audit portal designed to extract, validate, and route shipment trade documentation (such as Bills of Lading, Invoices, and Packing Lists). The platform automates checks against custom customer compliance rule sets, logs execution runs in a local SQLite database, allows manual operator-in-the-loop review overrides, and supports natural language database querying.

---

## 💡 The Problem It Solves

International trade compliance is highly document-intensive. Customs authorities and importers must audit multiple shipment documents (e.g., Bills of Lading, Commercial Invoices, Packing Lists) to verify compliance before cargo is allowed to cross borders. Historically, this process faces three major issues:
1. **Manual Inefficiency & Human Error:** Checking single documents against regulatory rules (like HS code prefix matching, allowed ports of origin, consignee details, and maximum weight limits) is slow and prone to errors.
2. **Cross-Document Discrepancies (Part 2):** Shipments usually come with multiple files (e.g., Bill of Lading, Invoice, Packing List). Discrepancies in core fields (for example, the gross weight in the Bill of Lading doesn't match the Packing List, or the Consignee Name contains spelling errors in one document but not the others) often lead to customs holds, delay penalties, and compliance fines.
3. **Complex Ingestion Streams:** Real-world documents arrive via email inboxes as clusters of attachments rather than clean, manual single-file uploads through a portal.

This platform solves these problems by executing a **Multi-Agent LangGraph Pipeline** that automatically ingests files via **Manual Uploads** or a **Simulated Supplier Email Queue**, runs deterministic compliance rules, compares fields across multiple documents to flag discrepancies, drafts correction/amendment emails automatically, and stores audit trails in SQLite which operators and managers can query using plain English.

---

## 🚀 Key Features & Updates (Part 2)

### 1. Multi-Agent Verification Pipeline (LangGraph)
* **Extractor Agent:** Utilizes **Gemini 2.5 Flash** (inline byte payloads) to extract structured parameters (consignee, HS code, weight, ports, incoterms, invoice number) from PDFs/images with confidence scores.
* **Validator Agent:**
  * **Deterministic Rule Matching:** Matches extracted data against a customer-specific `rules.json` rule set (supports exact, prefix, allow list, regex patterns, and numeric limit checks).
  * **Cross-Document Consistency Check (Part 2):** When a shipment consists of multiple files (e.g. Invoice + BOL + Packing List), the Validator automatically standardizes and compares values across files for core fields: `consignee_name`, `hs_code`, `gross_weight`, `incoterms`, and `invoice_number`. If normalized values differ, it flags a discrepancy, preventing blind approval.
* **Router Agent:** Classifies shipments into lanes (`auto_approve`, `flag_review`, or `amendment_request`) and invokes **Mistral AI** to generate reasoning summaries and email drafts to request document amendments from suppliers.

### 2. Dual Ingestion Modes & Background Watcher (Part 2)
* **Simulated Supplier Email Ingestion:** Rather than forcing manual upload, suppliers can submit documents via an email simulator.
* **Asynchronous Folder Watcher:** A background polling service (`watcher.py`) monitors an incoming `/inbox` folder. When it detects a new directory containing attachments and a `manifest.json` metadata trigger file, it triggers the LangGraph pipeline asynchronously in a background thread to process the documents.

### 3. Operator-in-the-Loop Review Console (Audit Desk)
* High-fidelity dark-mode UI highlighting compliance warnings, confidence scores, and cross-document mismatches.
* Allows manual override/editing of OCR values before final submission.
* Offers an interactive email editor to customize drafted supplier amendment notifications in case of failures.

### 4. Natural Language Database Query Assistant
* Translates plain English operational questions (e.g. *"Show me filenames of all runs that have weight mismatches"*) into SQL queries, executes them against SQLite, and summarizes findings in Markdown tables.

---

## 🖥️ Frontend Pages & Functionality

The frontend application consists of four key page views managed via a responsive dashboard layout:

### 1. Audit Desk (`AuditDesk.tsx`)
* **Purpose:** The primary operational dashboard where auditors process compliance runs.
* **Features:**
  * **Segmented Mode Toggle:** Switch between the **Supplier Mail Queue** view and **Manual Upload** view.
  * **Supplier Mail Queue (Part 2):** Lists runs received from simulated supplier emails. Divided into `Incoming` (active, unprocessed) and `Processed` (resolved) tabs.
  * **Real-time Pipeline Tracker:** Visually shows the active node step execution (`uploading` -> `extracting` -> `validating` -> `routing` -> `done`) and streams live server logs.
  * **Operator-in-the-Loop Review Panel:** When a run is selected, this panel displays:
    * **OCR Details:** Extracted data points with confidence color indicators (Green/Orange/Red).
    * **Compliance Results:** Output of the `rules.json` check.
    * **Cross-Document Discrepancies (Part 2):** Lists any fields containing mismatches across multiple uploaded files.
    * **Amendment Outbox:** An editable email compose pane populated with the AI-drafted supplier notification outlining the exact compliance failures.
    * **Actions:** Quick buttons to save edited values and update the shipment status (`approve`, `flag`, or `request amendment`).

### 2. Supplier Outbox Console (`SupplierPortal.tsx`)
* **Purpose:** Simulates a supplier sending shipping documents to the company's inbox.
* **Features:**
  * **Email Composer:** Input fields for sender email, subject line, and body message.
  * **Multi-file Drag and Drop Zone:** Supports attaching multiple PDFs and image files.
  * **Queuing Pipeline:** Submitting the form calls a backend endpoint that writes the attachments and metadata manifest to the `/inbox` folder to trigger the background watcher.

### 3. Run Registry (`HistoryRegistry.tsx`)
* **Purpose:** A centralized archival table for auditing historical shipments logged in the SQLite database.
* **Features:**
  * **Ingestion Source Labeling (Part 2):** Clear icons and badges indicating if a run came from Simulated Email or Manual Upload.
  * **Cross-Document Check Summary (Part 2):** Displays a green "Consistent" badge or a red "Mismatch" warning badge with the count of discrepancies.
  * **Quick Audit Action:** Clicking "Audit" instantly loads the history record back into the Audit Desk console for review.

### 4. NL Query Assistant (`NLQueryAssistant.tsx`)
* **Purpose:** Empowers non-technical team members to perform complex database querying using plain English.
* **Features:**
  * Quick-select example query chips (e.g. *"List filenames of documents that require review"*).
  * Text area for entering custom queries.
  * **SQL Code Toggle:** Reveals the exact SQL query generated by the AI model.
  * **Visual Table Grid:** Renders results dynamically in a tabular display with a markdown summary.

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
│   ├── controllers/          # Modular API request handlers (upload, status, query, trigger)
│   ├── graph/                # LangGraph state machine workflow
│   ├── helpers/              # Database assistants, router & validator helpers
│   ├── routes/               # API endpoint routing (pipeline & email triggers)
│   ├── services/             # SQLite storage and NL SQL query translation, Background Watcher
│   ├── sample_docs/          # Test PDF invoices
│   └── app.py                # App entrypoint & Background watcher startup
├── client/                   # React Application
│   ├── src/
│   │   ├── api/              # Modular API fetch handlers
│   │   ├── components/       # SideBar, AnalyticsCards, ReviewPanel, etc.
│   │   ├── pages/            # Page Views (AuditDesk, HistoryRegistry, NLQueryAssistant, SupplierPortal)
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
# Backend (new terminal)
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn app:app --reload
```
* The backend will run on `http://127.0.0.1:8000/`.
* The background email watcher will automatically start polling the `inbox/` folder.

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

## 🧪 Testing the Pipeline via cURL (Manual Email Simulation)

You can bypass the UI and simulate an email trigger via a POST request to `/pipeline/incoming`:

```powershell
curl.exe -X POST "http://127.0.0.1:8000/pipeline/incoming" `
  -H "accept: application/json" `
  -H "Content-Type: multipart/form-data" `
  -F "sender=supplier@globalshipping.com" `
  -F "subject=Urgent: Shipment Docs for PO#8892" `
  -F "email_body=Dear Team, attached are the Invoice and Packing List for the upcoming trade shipment. Please process." `
  -F "file=@backend/sample_docs/clean_invoice.pdf"
```

---

## 🚢 Deployment Guide

For deploying the platform in a production environment, there are two primary methods:

### Method 1: Containerized Deployment (Docker Compose) - *Recommended*

This is the easiest and most robust method. It sets up both services, manages directory permissions, handles database persistence volumes, and proxies API calls securely.

1. **Configure Environment Variables:**
   Ensure the `backend/.env` file is populated with valid credentials (`GEMINI_API_KEY`, `MISTRAL_API_KEY`, etc.).

2. **Launch Services:**
   From the root folder containing `docker-compose.yml`, run:
   ```bash
   docker-compose up -d --build
   ```

3. **Verify Running Containers:**
   ```bash
   docker-compose ps
   ```
   * **Frontend UI Console:** Available at `http://localhost:3000`
   * **Backend REST API:** Available at `http://localhost:8000`
   * **Watcher Ingestion Directories:** Automatically managed and persisted via named Docker volumes (`sqlite_data`, `watcher_inbox`, and `watcher_processed`).

---

### Method 2: Manual Server Deployment (VPS / EC2 Instance)

For deploying manually onto a Linux server (e.g., Ubuntu):

#### 1. Setup Backend
* Clone the codebase, set up a virtual environment, and install dependencies:
  ```bash
  cd backend
  python3 -m venv venv
  source venv/bin/activate
  pip install -r requirements.txt
  ```
* Run Uvicorn in the background using a process manager like **PM2** or **systemd**:
  ```bash
  pm2 start "uvicorn app:app --host 0.0.0.0 --port 8000" --name "trade-compliance-backend"
  ```
  *(The background inbox watcher starts automatically on application startup.)*

#### 2. Setup Frontend
* Install Node.js, install client dependencies, and build static production assets:
  ```bash
  cd ../client
  npm install
  npm run build
  ```
  This creates a production folder `client/dist/`.

#### 3. Setup Reverse Proxy (Nginx)
Install Nginx and configure a server block (e.g. `/etc/nginx/sites-available/default`) to serve the built static assets and proxy API endpoints:

```nginx
server {
    listen 80;
    server_name your_domain_or_ip;

    # Serve built React static assets
    location / {
        root /path/to/go-comet/assignment/client/dist;
        index index.html index.htm;
        try_files $uri $uri/ /index.html;
    }

    # Proxy pipeline API calls to Uvicorn running on 8000
    location /pipeline {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```
* Restart Nginx:
  ```bash
  sudo systemctl restart nginx
  ```

