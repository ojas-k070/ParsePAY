# Bank Statement Analysis Application

A Flask-based web application to parse bank statements in PDF format, extract transactions and opening/closing balances, classify transaction categories using Naive Bayes machine learning and keyword matching, and export the processed data to CSV/Excel.

---

## Getting Started

Follow these steps to set up and start the application on your machine.

### Prerequisites

Ensure you have **Python 3.8+** installed on your system. You can verify this by running:
```bash
python --version
```

---

## Startup Steps (Windows)

Since the project source files are located in the `ASEP_2_Bank_Statement` directory, follow these steps from the root directory (`e:\Bank statement analysis`):

### Step 1: Navigate to the Project Directory
Open your terminal/command prompt and move into the project subfolder:
```powershell
cd ASEP_2_Bank_Statement
```

### Step 2: Activate the Virtual Environment
An existing virtual environment (`venv`) is already present inside the project folder. Activate it by running:
* **Command Prompt (cmd):**
  ```cmd
  venv\Scripts\activate
  ```
* **PowerShell:**
  ```powershell
  .\venv\Scripts\activate
  ```

> [!NOTE]
> If you get a script execution policy error in PowerShell, you can run: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` first, or use the Command Prompt.

### Step 3: Install Dependencies
If you haven't installed the required Python packages yet (or want to make sure they are up-to-date), run:
```bash
pip install -r requirements.txt
```

### Step 4: Run the Application
You can start the web server in one of two ways:

#### Option A: Running the WSGI wrapper script (Recommended)
```bash
python wsgi.py
```

#### Option B: Running directly with Flask CLI
* **Command Prompt (cmd):**
  ```cmd
  set FLASK_APP=extractpdf.py
  set FLASK_ENV=development
  flask run
  ```
* **PowerShell:**
  ```powershell
  $env:FLASK_APP="extractpdf.py"
  $env:FLASK_ENV="development"
  flask run
  ```

---

## Startup Steps (macOS / Linux)

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

## Accessing the Web Interface

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
