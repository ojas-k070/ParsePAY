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
* **Smart Reconciliation:** Custom filtering logic to identify and net out internal self-transfers (e.g., wallet loads, bank-to-bank transfers), preventing the artificial inflation of income and expense metrics.
* **Schema Normalization:** Converts messy, varying bank statement formats into a standard, clean schema for deep analytics.

## 🛠 Tech Stack

* **Backend:** Python, Flask
* **Data Extraction:** `pdfplumber`, `PyPDF2`
* **Intelligence:** Scikit-Learn (Naive Bayes/Random Forest for classification)
* **Storage:** SQLite/PostgreSQL (for persistent keyword-to-category mapping)

## 💡 Engineering Highlights
* **Separation of Concerns:** The system architecture separates the *data extraction layer* from the *business intelligence layer*, making it modular and adaptable to new bank statement formats.
* **Data Integrity:** By implementing a persistent database for category mapping, the system "learns" user preferences across sessions, reducing manual categorization.
* **Noise Reduction:** Unlike basic ledger tools, ParsePAY distinguishes between genuine market transactions and internal account settlements, providing an accurate view of spending.

## 📦 How to Run

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/parsepay.git](https://github.com/yourusername/parsepay.git)
2.**Install dependencies:**
pip install -r requirements.txt

3.**Run the application:**
python app.py
4.**Access the Dashboard:**
Open http://127.0.0.1:5000 in your browser.
