<div align="center">

# ParsePAY
*Intelligent Financial Intelligence Platform*

[![Python](https://img.shields.io/badge/python-3.x-blue.svg)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/flask-2.x-lightgrey.svg)](https://flask.palletsprojects.com/)
[![Status](https://img.shields.io/badge/status-active-green.svg)]()

</div>

## 📖 Overview
**ParsePAY** is an AI-powered financial reconciliation platform designed to solve the problem of fragmented banking data. Traditional finance tools often struggle with inconsistent bank statement formats and "noisy" data like internal transfers. ParsePAY normalizes these inputs, intelligently categorizes transactions, and provides clear insights into actual personal cash flow.

## 🚀 Key Features

* **Universal Parsing Engine:** Decouples raw document ingestion from financial logic, supporting heterogeneous PDF layouts.
* **Persistent ML Categorization:** A learning-based classification layer that remembers manual user overrides, improving accuracy over time.
* **Smart Reconciliation:** Custom filtering logic to identify and net out self-transfers (e.g., wallet loads, bank-to-bank transfers), preventing the artificial inflation of income and expense metrics.
* **Schema Normalization:** Converts messy, varying bank statement formats into a standard, clean schema for deep analytics.

## 🛠 Tech Stack

* **Backend:** Python, Flask
* **Data Extraction:** `pdfminer.six` / Layout analysis
* **Intelligence:** Scikit-Learn (Naive Bayes for classification)
* **Frontend:** React SPA (Vite, Chart.js, Vanilla CSS)
* **Storage:** SQLite (for persistent keyword-to-category mapping)

## 💡 Engineering Highlights
* **Separation of Concerns:** The system architecture separates the *data extraction layer* from the *business intelligence layer*, making it modular and adaptable to new bank statement formats.
* **Data Integrity:** By implementing a persistent database for category mapping, the system "learns" user preferences across sessions, reducing manual categorization.
* **Noise Reduction:** Unlike basic ledger tools, ParsePAY distinguishes between genuine market transactions and internal account settlements, providing an accurate view of spending.

---

## ⚙️ Setup & Installation

Follow these steps to set up and start the application on your machine.

### Prerequisites
Ensure you have **Python 3.8+** installed on your system. You can verify this by running:
```bash
python --version
```

### Windows Setup

Since the project source files are located in the `ASEP_2_Bank_Statement` directory, follow these steps from the root directory (`e:\Bank statement analysis`):

1. **Navigate to the Project Directory:**
   ```powershell
   cd ASEP_2_Bank_Statement
   ```

2. **Activate the Virtual Environment:**
   An existing virtual environment (`venv`) is already present inside the project folder. Activate it by running:
   * **Command Prompt (cmd):**
     ```cmd
     venv\Scripts\activate
     ```
   * **PowerShell:**
     ```powershell
     .\venv\Scripts\activate
     ```
     *(If you get a script execution policy error in PowerShell, run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first)*

3. **Install Dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the Application:**
   ```bash
   python wsgi.py
   ```

### macOS / Linux Setup

If you are running on macOS or Linux, follow these commands from the root directory:

1. **Navigate to the directory:**
   ```bash
   cd ASEP_2_Bank_Statement
   ```
2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```
   *(If you need to recreate it, run `python3 -m venv venv` first)*
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
4. **Run the application:**
   ```bash
   python wsgi.py
   ```

---

## 💻 Accessing the Web Interface

Once the server has started, open your web browser and navigate to:
```
http://127.0.0.1:5000/
```

### How to Use
1. **Create a Profile:** Start by entering a username to generate a unique Profile ID (e.g., `RS-1234`).
2. **Login:** Use your Profile ID to login.
3. **Upload PDF:** Upload your bank statement PDF (e.g., HDFC, ICICI, SBI statements, etc.).
4. **Analyze Dashboard:** View categorized transactions, monthly charts, and daily spending habits.
5. **Download Reports:** Export parsed transactions to CSV or Excel formats from the dashboard.
