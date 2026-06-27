# 💳 ParsePAY – Intelligent Financial Intelligence Platform

<div align="center">

### 🚀 Transforming Raw Bank Statements into Actionable Financial Insights

![Python](https://img.shields.io/badge/Python-3.11-blue?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/Flask-Backend-black?style=for-the-badge&logo=flask)
![React](https://img.shields.io/badge/React-Frontend-61DAFB?style=for-the-badge&logo=react)
![Machine Learning](https://img.shields.io/badge/Machine%20Learning-TFIDF%20%2B%20Naive%20Bayes-green?style=for-the-badge)
![SQLite](https://img.shields.io/badge/Database-SQLite-blue?style=for-the-badge&logo=sqlite)

### Parse • Categorize • Analyze • Export

</div>

---

## 📖 About ParsePAY

ParsePAY is an AI-powered financial analytics platform that automatically converts raw bank statements into meaningful financial insights. It intelligently parses PDF statements, extracts transactions, categorizes expenses using Machine Learning, visualizes spending patterns, and generates professional Excel reports.

The platform is designed to eliminate manual expense tracking and provide users with an intelligent and self-improving financial management system.

---

## ✨ Features

✅ Smart PDF Bank Statement Parsing  
✅ Automatic Opening & Closing Balance Extraction  
✅ Intelligent Transaction Categorization using Machine Learning  
✅ Interactive Financial Dashboard & Analytics  
✅ Professional Excel Report Generation  
✅ Hybrid Rule-Based + AI Classification System  
✅ Active Learning for Continuous Improvement  
✅ User Custom Category Mapping  
✅ Dark & Light Mode UI  
✅ Responsive Web Application

---

# 📸 Application Screenshots

## Landing Page
<img width="1919" height="971" alt="image" src="https://github.com/user-attachments/assets/7304f4bc-74f9-464f-9e99-1438c983a454" />
<img width="1919" height="971" alt="image" src="https://github.com/user-attachments/assets/6245d76e-844a-4aa2-be71-d9ebe9bd2be2" />


## Dashboard
<img width="1916" height="968" alt="image" src="https://github.com/user-attachments/assets/00ce708e-4126-46cc-900e-29793b28004f" />


## Analytics Page
<img width="1916" height="858" alt="image" src="https://github.com/user-attachments/assets/afd796c0-1c35-4acd-9168-0f33bcca8667" />


## Transaction Categorization
<img width="1917" height="973" alt="image" src="https://github.com/user-attachments/assets/38e128ca-58f4-479d-9806-cb783e7c8f9c" />
<img width="1919" height="969" alt="image" src="https://github.com/user-attachments/assets/c50a823a-b1ee-4a42-a92f-0353fb6c48b7" />


## Excel Export
<img width="1634" height="815" alt="image" src="https://github.com/user-attachments/assets/978e3f33-83b0-485f-8986-4b4a3def1d73" />


---

# 🏗️ System Architecture

```text
PDF Statement
      ↓
PDF Extraction Engine
      ↓
Transaction Cleaning & Normalization
      ↓
Machine Learning Classification
      ↓
Financial Analytics Dashboard
      ↓
Excel Report Generation
```

---

# 🧠 Machine Learning Pipeline

```text
Explicit Mappings
       ↓
Machine Learning Prediction
       ↓
Rule-Based Classification
       ↓
Review Needed
```

The system uses a multi-tier categorization pipeline to maximize accuracy and minimize manual intervention.

### Technologies Used

- TF-IDF Vectorization
- Multinomial Naive Bayes Classifier
- Confidence Thresholding
- Background Model Retraining
- Active Learning Feedback Loop

---

# 🔄 Active Learning Workflow

```text
User Corrects Category
          ↓
Database Updated
          ↓
Background Retraining
          ↓
Model Serialized
          ↓
Future Predictions Improved
```

The system continuously improves its categorization accuracy by learning from user corrections.

---

# ⚙️ Tech Stack

## Backend
- Python
- Flask
- SQLAlchemy
- SQLite

## Frontend
- React (Vite)
- HTML5
- CSS3
- JavaScript
- Chart.js

## Data Processing
- Pandas
- OpenPyXL
- pdfminer.six
- Regex Processing

## Machine Learning
- Scikit-Learn
- TF-IDF Vectorizer
- Multinomial Naive Bayes

## Deployment
- Render Cloud
- Free Sandbox Environment

---

# 🗄️ Database Design

### User Table
Stores user profiles and unique profile IDs.

### UploadedFile Table
Stores uploaded statement metadata and balance information.

### Transaction Table
Stores parsed transaction details including:
- Date
- Particulars
- Debit Amount
- Credit Amount
- Category
- Manual Override Flag

### SavedMapping Table
Stores custom merchant-category mappings created by users.

---

# 📊 Dashboard Features

- Total Income & Expenses
- Category-wise Expense Distribution
- Spending Trends
- Cash Flow Analysis
- Financial Summary Cards
- Interactive Charts
- Dynamic Filters

---

# 📥 Excel Report Generation

ParsePAY generates professional multi-sheet Excel reports including:

- Categorized Transactions
- Expense Summary
- Category Analytics
- Styled Sheets
- Formula Support
- Downloadable Reports

---

# 🚀 Key Innovations

✔ Hybrid Rule-Based + Machine Learning Categorization

✔ Automatic Merchant Name Normalization

✔ Dynamic Model Retraining

✔ Active Learning Feedback Loop

✔ Professional Financial Reconciliation Reports

✔ Intelligent Financial Analytics Dashboard

✔ Self-Improving Categorization Engine

---

# 📂 Project Structure

```text
ParsePAY
│
├── README.md
├── .gitignore
└── ASEP_2_Bank_Statement
    ├── extractpdf.py
    ├── wsgi.py
    ├── render.yaml
    ├── requirements.txt
    ├── ParsePAY_Technical_Report.pdf
    ├── .gitignore
    │
    ├── uploads/
    │   └── Raw uploaded bank statement PDFs
    │
    ├── processed/
    │   └── Generated CSV & Excel reports
    │
    ├── instance/
    │   ├── SQLite databases
    │   └── Trained ML model caches
    │
    ├── venv/
    │   └── Python virtual environment
    │
    ├── static/
    │   └── Built React frontend assets
    │
    └── frontend/
        ├── index.html
        ├── package.json
        ├── vite.config.js
        ├── public/
        │
        └── src/
            ├── main.jsx
            ├── App.jsx
            ├── index.css
            │
            ├── components/
            │   ├── Sidebar.jsx
            │   └── SupportPopup.jsx
            │
            ├── context/
            │   ├── AuthContext.jsx
            │   └── ThemeContext.jsx
            │
            └── pages/
                ├── Login.jsx
                ├── Upload.jsx
                └── Dashboard.jsx
```

## 🔑 Key Components

### 🐍 Backend
- **extractpdf.py** → Core Flask server containing:
  - PDF parsing engine
  - Database models
  - Transaction categorization logic
  - Machine Learning pipeline
  - REST APIs

- **wsgi.py** → Production WSGI entry point.

- **render.yaml** → Render deployment configuration.

---

### ⚛️ Frontend
- **Login.jsx** → User profile authentication and registration.
- **Upload.jsx** → Bank statement upload interface.
- **Dashboard.jsx** → Financial analytics dashboard with charts, transaction tables, and spending insights.
- **ThemeContext.jsx** → Global dark/light theme management.
- **AuthContext.jsx** → User authentication state management.

---

### 🤖 Machine Learning
- TF-IDF Vectorization
- Multinomial Naive Bayes Classifier
- Active Learning Feedback Loop
- Dynamic Model Retraining
- Merchant Name Normalization Engine

---

### 📊 Data Processing
- PDF Statement Extraction
- Transaction Cleaning & Normalization
- Opening & Closing Balance Detection
- Financial Analytics Generation
- Professional Excel Report Export

# 🚀 Installation & Setup

### Clone Repository

```bash
git clone https://github.com/yourusername/ParsePAY.git
cd ParsePAY
```

### Backend Setup

```bash
pip install -r requirements.txt
python app.py
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

---

# 🔮 Future Enhancements

- Multi-Bank Statement Support
- AI-Based Spending Prediction
- Budget Recommendation System
- Fraud Detection System
- Mobile Application
- OCR Support for Scanned Statements
- Personalized Financial Insights
- Smart Savings Suggestions

---

# 👨‍💻 Developed By

## Ojas Kulkarni
B.Tech Artificial Intelligence Engineering {Extended version of SEM-1 Project} 
Vishwakarma Institute of Technology, Pune

---

<div align="center">

## ⭐ Star this repository if you found it useful!

### "Turning Raw Bank Statements into Intelligent Financial Insights."

</div>
