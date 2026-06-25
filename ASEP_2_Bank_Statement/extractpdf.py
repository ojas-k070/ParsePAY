import csv
import os
import pickle
import random
import re
import string
from datetime import datetime
from decimal import Decimal, ROUND_HALF_UP
from functools import wraps
from io import StringIO

import pandas as pd
from flask import Flask, render_template, request, redirect, flash, send_file, jsonify, session, g
from flask_sqlalchemy import SQLAlchemy
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecretkey'
app.config['UPLOAD_FOLDER'] = r"./uploads"
app.config['PROCESSED_FOLDER'] = r"./processed"
app.config['ALLOWED_EXTENSIONS'] = {'pdf'}
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# Ensure folders exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
os.makedirs(app.config['PROCESSED_FOLDER'], exist_ok=True)
os.makedirs(app.instance_path, exist_ok=True)

MODEL_PATH = os.path.join(app.instance_path, 'ml_model.pkl')

# Database models
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), nullable=False)
    unique_id = db.Column(db.String(10), unique=True, nullable=False)
    uploaded_files = db.relationship('UploadedFile', backref='user', lazy=True, cascade="all, delete-orphan")
    saved_mappings = db.relationship('SavedMapping', backref='user', lazy=True, cascade="all, delete-orphan")

class UploadedFile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(120), nullable=False)
    upload_time = db.Column(db.DateTime, default=datetime.utcnow)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    opening_balance = db.Column(db.Float, default=0.0)
    closing_balance = db.Column(db.Float, default=0.0)
    transactions = db.relationship('Transaction', backref='file', lazy=True, cascade="all, delete-orphan")

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    file_id = db.Column(db.Integer, db.ForeignKey('uploaded_file.id'), nullable=False)
    date = db.Column(db.String(10), nullable=False) # DD-MM-YYYY
    particulars = db.Column(db.String(500), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    withdrawal = db.Column(db.Float, default=0.0)
    deposit = db.Column(db.Float, default=0.0)
    is_manual = db.Column(db.Boolean, default=False)

class SavedMapping(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    merchant = db.Column(db.String(255), nullable=False)
    category = db.Column(db.String(100), nullable=False)
    __table_args__ = (db.UniqueConstraint('user_id', 'merchant', name='_user_merchant_uc'),)

def generate_unique_user_id():
    """Generate a unique random alphanumeric profile ID (e.g., RS-4927)."""
    while True:
        uid = "RS-" + "".join(random.choices(string.digits, k=4))
        # Use modern db.session.scalar to check existence
        exists = db.session.scalar(db.select(User).filter_by(unique_id=uid))
        if not exists:
            return uid

def categorize_transaction(particulars):
    """Categorize transaction using rule-based keywords."""
    p_upper = particulars.upper()
    
    # Medical & Healthcare (Medicines, Hospitals, Doctor consultation, diagnostics)
    if any(k in p_upper for k in [
        'APOLLO', 'PHARMACY', 'MEDICINE', 'HOSPITAL', 'CLINIC', 'MEDPLUS', 'NETMEDS', 
        'PHARMEASY', 'DOCTOR', 'HEALTHCARE', 'DENTAL', 'DIAGNOSTIC', 'LABS', 'SURGERY', 
        'CHEMIST', 'DR.', 'CLINICAL', 'DENTIST', 'OPTICAL', 'LENSKART', 'PHYSIO', 'MEDICOS', 'MEDIC'
    ]):
        return 'Medical & Healthcare'
        
    # Entertainment & Subscriptions
    if any(k in p_upper for k in [
        'NETFLIX', 'SPOTIFY', 'BOOKMYSHOW', 'HOTSTAR', 'YOUTUBE PREMIUM', 'PRIME VIDEO', 
        'PLAYSTATION', 'STEAM', 'GAMING', 'THEATRE', 'CINEMA', 'JIO SAAVN', 'MUSIC',
        'SONYLIV', 'ZEE5', 'APPLE.COM/BILL', 'APPLE SERVICES', 'GOOGLE PLAY', 'PVR', 'INOX',
        'TICKET', 'EVENT', 'DISNEY'
    ]):
        return 'Entertainment & Subscriptions'
        
    # Rent & Maintenance
    if any(k in p_upper for k in ['RENT', 'MAINTENANCE', 'SOCIETY', 'FLAT', 'HOUSE RENT', 'PG PAY', 'LANDLORD', 'HOSTEL', 'NOBROKER', 'MAINT']):
        return 'Rent & Maintenance'
        
    # Education
    if any(k in p_upper for k in [
        'FEES', 'SCHOOL', 'COLLEGE', 'TUITION', 'UDEMY', 'COURSERA', 'BOOKS', 'STATIONERY', 
        'ACADEMY', 'INSTITUTE', 'CLASSES', 'BYJUS', 'UNACADEMY', 'PHYSICS WALLAH', 'SIMPLILEARN', 
        'EDX', 'XEROX', 'PHOTOCOPY'
    ]):
        return 'Education'
    
    # Food & Dining
    if any(k in p_upper for k in [
        'ZOMATO', 'SWIGGY', 'RESTAURANT', 'FOOD', 'CAFE', 'DOMINOS', 'PIZZA', 'EATCLUB', 'DINING',
        'STARBUCKS', 'SUBWAY', 'KFC', 'MCDONALD', 'BURGER KING', 'HALDIRAM', 'BIRYANI', 'BAKERY', 
        'CHAI', 'COFFEE', 'HOTEL', 'DHABA', 'DABA', 'BAR', 'BREWERY', 'PIZZERIA', 'BOX8', 'MOJO PIZZA', 
        'PIZZA HUT', 'TACO BELL', 'EATURE', 'SWEET', 'IRANI CHAI'
    ]):
        return 'Food & Dining'
    
    # Shopping
    if any(k in p_upper for k in [
        'AMAZON', 'FLIPKART', 'MYNTRA', 'RETAIL', 'AJIO', 'SHOPPING', 'SPAR', 'DMART', 'GROCERY', 
        'SUPERMARKET', 'BLINKIT', 'ZEPTO', 'INSTAMART', 'BIGBASKET', 'DUNZO', 'MILKBASKET', 
        'COUNTRY DELIGHT', 'JIO MART', 'JIOMART', 'MEESHO', 'NYKAA', 'TATA CLIQ', 'DECATHLON', 
        'ZARA', 'H&M', 'UNIQLO', 'LIFESTYLE', 'MAX RETAIL', 'TRENDS', 'RELIANCE TRENDS', 'WESTSIDE', 
        'MALL', 'STORE', 'SUPER MARKET', 'MART', 'PROVISIONS', 'APPAREL', 'CLOTHING', 'FOOTWEAR', 
        'JEWELLER', 'KIRANA', 'MILK', 'AMUL', 'MOTHER DAIRY', 'SUPER STORE'
    ]):
        return 'Shopping'
    
    # Salary / Income (Deposits)
    if any(k in p_upper for k in ['SALARY', 'DIVIDEND', 'INTEREST CREDITED', 'INT.PD', 'SCHEME', 'REIMBURSE', 'CASHBACK', 'REFUND']):
        return 'Salary & Income'
    
    # Bills, Utilities & Subscriptions
    if any(k in p_upper for k in [
        'ELECTRICITY', 'TELEPHONE', 'MOBILE', 'RECHARGE', 'BROADBAND', 'INSUR', 'LIC', 'BILLPAY', 
        'GAS', 'DTH', 'WATER BILL', 'BESCOM', 'MSEB', 'MSEDCL', 'UPPCL', 'TNEB', 'BSNL', 'AIRTEL', 
        'JIO', 'VI ', 'VODAFONE', 'IDEA', 'ACT FIBER', 'HATHWAY', 'INSURANCE', 'HDFC ERGO', 
        'ICICI LOMBARD', 'MAX LIFE', 'SBI LIFE', 'FASTAG', 'TOLL', 'WIFI', 'WI-FI', 'POWER', 'DISCOM',
        'TATAPLAY', 'TATA PLAY'
    ]):
        return 'Bills & Utilities'
    
    # Investment
    if any(k in p_upper for k in [
        'MUTUAL FUND', 'INDMONEY', 'ZERODHA', 'GROWW', 'STOCK', 'SIP', 'NPS', 'PPF', 'COIN', 
        'WZRX', 'COINDCX', 'KUBER', 'BINANCE', 'GOLD', 'SECURITIES', 'BROKER', 'UPSTOX', 'ANGELONE', 
        'ANGEL BROKING', '5PAISA', 'FINVASIA', 'MOTILAL', 'SHAREKHAN'
    ]):
        return 'Investment'
        
    # Travel & Fuel
    if any(k in p_upper for k in [
        'UBER', 'OLA', 'PETROLEUM', 'HPCL', 'BPCL', 'IOCL', 'FUEL', 'IRCTC', 'METRO', 'FLIGHT', 
        'TRAVEL', 'RAPIDO', 'NAMMAYATRI', 'NAMMA YATRI', 'BLUSMART', 'MAKEMYTRIP', 'MMT', 'GOIBIBO', 
        'YATRA', 'EASEMYTRIP', 'AIR INDIA', 'INDIGO', 'SPICEJET', 'AKASA', 'RAILWAY', 'BUS', 
        'REDBUS', 'RED BUS', 'KSRTC', 'MSRTC', 'AUTO', 'CAB', 'TAXI', 'SHELL', 'HP FUEL', 'IOC FUEL', 
        'BP FUEL', 'GAS STATION'
    ]):
        return 'Travel & Fuel'
        
    # Cash Withdrawal
    if any(k in p_upper for k in ['ATM', 'CASH WDL', 'CASH WITHDRAWAL', 'WDL', 'WITHDRWL']):
        return 'Cash Withdrawal'

    # Transfers / UPI (Generic)
    # Recognize clean UPI transactions (starts with 'DR / ' or 'CR / ') and general transfer patterns
    if (particulars.startswith('DR / ') or particulars.startswith('CR / ') or 
        any(k in p_upper for k in ['UPI', 'NEFT', 'IMPS', 'RTGS', 'TRANSFER', 'GPAY', 'PAYTM', 'PHONEPE', 'BHIM', 'PAY TO', 'SENT TO', 'RECEIVED FROM'])):
        return 'Transfer'
        
    return 'Other'

def get_merchant_key(particulars):
    """Normalize and extract a merchant key from transaction particulars."""
    parts = [p.strip() for p in particulars.split('/')]
    if len(parts) >= 3 and parts[0] in ('DR', 'CR'):
        # Cleaned UPI format: DR / MERCHANT NAME / BANK NAME / UPI ID
        # Return the merchant name part (uppercased)
        return parts[1].upper()
    return particulars.upper()

def train_classifier():
    """Train the Naive Bayes classifier on current transaction and custom mapping data."""
    try:
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.naive_bayes import MultinomialNB
        from sklearn.pipeline import Pipeline

        # Query all categorized transactions (excluding low confidence defaults unless manually reviewed)
        txs = Transaction.query.filter(Transaction.category != 'Other').all()
        # Also query all custom user hard-mappings
        mappings = SavedMapping.query.all()

        texts = []
        labels = []

        # Bootstrap with categorized transactions (using extracted merchant keys)
        for tx in txs:
            texts.append(get_merchant_key(tx.particulars))
            labels.append(tx.category)

        # Boost the custom mappings (give them more sample representation or simple add)
        for m in mappings:
            texts.append(m.merchant)
            labels.append(m.category)

        if len(set(labels)) < 2:
            print("ML_TRAIN: Too few classes (< 2) to train Naive Bayes. Skipping.", flush=True)
            return False

        pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(ngram_range=(1, 2), token_pattern=r'(?u)\b\w+\b')),
            ('nb', MultinomialNB(fit_prior=False))
        ])
        pipeline.fit(texts, labels)

        # Save model to disk
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(pipeline, f)
        print(f"ML_TRAIN: Model trained successfully with {len(texts)} samples across {len(set(labels))} classes.", flush=True)
        return True
    except Exception as e:
        print("ML_TRAIN: Error training Naive Bayes classifier:", e, flush=True)
        return False

_classifier = None

def load_classifier():
    global _classifier
    if os.path.exists(MODEL_PATH):
        try:
            with open(MODEL_PATH, 'rb') as f:
                _classifier = pickle.load(f)
        except Exception as e:
            print("ML_LOAD: Error loading classifier pickle:", e, flush=True)
            _classifier = None

def predict_category(particulars):
    """Predict category for transaction particulars using the ML model.
    Returns (predicted_category, confidence) or (None, 0.0).
    """
    global _classifier
    if _classifier is None:
        load_classifier()
    if _classifier is None:
        return None, 0.0

    try:
        # Predict probability using extracted merchant key
        merchant_key = get_merchant_key(particulars)
        probs = _classifier.predict_proba([merchant_key])[0]
        classes = _classifier.classes_
        max_idx = probs.argmax()
        confidence = float(probs[max_idx])
        category = classes[max_idx]
        return category, confidence
    except Exception as e:
        print("ML_PREDICT: Error in Naive Bayes prediction:", e, flush=True)
        return None, 0.0

def extract_balances(text):
    """Extract opening and closing balances from PDF text."""
    opening_bal = 0.0
    closing_bal = 0.0
    
    lines = text.split('\n')
    
    # 1. Search for Opening Balance
    for idx, line in enumerate(lines):
        line_clean = line.strip()
        match = re.search(r'Your Opening Balance on \d{2}-\d{2}-\d{2,4}:\s*([\d,]+\.\d{2})', line_clean, re.IGNORECASE)
        if match:
            opening_bal = float(match.group(1).replace(',', ''))
            break
        elif re.search(r'Your Opening Balance on \d{2}-\d{2}-\d{2,4}:', line_clean, re.IGNORECASE):
            found = False
            for offset in range(1, 12):
                if idx + offset < len(lines):
                    sub_line = lines[idx + offset].strip()
                    val_match = re.search(r'(?:Rs\.?|INR)?\s*([\d,]+\.\d{2})\s*(?:Cr|Dr)?', sub_line, re.IGNORECASE)
                    if val_match:
                        try:
                            opening_bal = float(val_match.group(1).replace(',', ''))
                            found = True
                            break
                        except ValueError:
                            continue
            if found:
                break

    # 2. Search for Closing Balance
    for idx, line in enumerate(lines):
        line_clean = line.strip()
        match = re.search(r'Your Closing Balance on \d{2}-\d{2}-\d{2,4}:\s*([\d,]+\.\d{2})', line_clean, re.IGNORECASE)
        if match:
            closing_bal = float(match.group(1).replace(',', ''))
            break
        elif re.search(r'Your Closing Balance on \d{2}-\d{2}-\d{2,4}:', line_clean, re.IGNORECASE):
            found = False
            for offset in range(1, 12):
                if idx + offset < len(lines):
                    sub_line = lines[idx + offset].strip()
                    val_match = re.search(r'(?:Rs\.?|INR)?\s*([\d,]+\.\d{2})\s*(?:Cr|Dr)?', sub_line, re.IGNORECASE)
                    if val_match:
                        try:
                            closing_bal = float(val_match.group(1).replace(',', ''))
                            found = True
                            break
                        except ValueError:
                            continue
            if found:
                break
                
    return opening_bal, closing_bal

# Ensure database tables are created on the first request
first_request_executed = False

@app.before_request
def create_tables():
    global first_request_executed
    if not first_request_executed:
        db.create_all()
        
        # Add opening_balance and closing_balance columns if not present
        try:
            db.session.execute(db.text("ALTER TABLE uploaded_file ADD COLUMN opening_balance FLOAT DEFAULT 0.0"))
            db.session.execute(db.text("ALTER TABLE uploaded_file ADD COLUMN closing_balance FLOAT DEFAULT 0.0"))
            db.session.commit()
            print("MIGRATION: Added opening_balance and closing_balance columns to uploaded_file table.", flush=True)
        except Exception:
            db.session.rollback()

        # Add is_manual column to transaction if not present
        try:
            db.session.execute(db.text('ALTER TABLE "transaction" ADD COLUMN is_manual BOOLEAN DEFAULT 0'))
            db.session.commit()
            print("MIGRATION: Added is_manual column to transaction table.", flush=True)
        except Exception:
            db.session.rollback()
            
        # Run one-time migration to upgrade existing 'Other' transactions
        try:
            txs = Transaction.query.filter_by(category='Other').all()
            print(f"MIGRATION: Found {len(txs)} transactions with 'Other' category.", flush=True)
            updated = False
            for tx in txs:
                new_cat = categorize_transaction(tx.particulars)
                if new_cat != 'Other':
                    print(f"MIGRATION: Updating '{tx.particulars}' from 'Other' -> '{new_cat}'", flush=True)
                    tx.category = new_cat
                    updated = True
            if updated:
                db.session.commit()
                print("MIGRATION: Database committed successfully.", flush=True)
        except Exception as e:
            print("Database migration error (Other category):", e, flush=True)
            
        # Populate opening and closing balances for existing statements
        try:
            files = UploadedFile.query.all()
            updated_files = False
            for f in files:
                if (f.opening_balance is None or f.opening_balance == 0.0) and (f.closing_balance is None or f.closing_balance == 0.0):
                    file_path = os.path.join(app.config['UPLOAD_FOLDER'], f.filename)
                    if os.path.exists(file_path):
                        rsrcmgr = PDFResourceManager()
                        retstr = StringIO()
                        codec = 'utf-8'
                        laparams = LAParams()
                        device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
                        fp = open(file_path, 'rb')
                        interpreter = PDFPageInterpreter(rsrcmgr, device)
                        for page in PDFPage.get_pages(fp):
                            interpreter.process_page(page)
                        text = retstr.getvalue()
                        fp.close()
                        device.close()
                        retstr.close()
                        
                        op_bal, cl_bal = extract_balances(text)
                        f.opening_balance = op_bal
                        f.closing_balance = cl_bal
                        updated_files = True
                        print(f"MIGRATION: Populated balance for {f.filename}: Op={op_bal}, Cl={cl_bal}", flush=True)
            if updated_files:
                db.session.commit()
                print("MIGRATION: Saved balances to database.", flush=True)
        except Exception as e:
            print("Migration error populating balances:", e, flush=True)
            
        # Bootstrap ML model training
        try:
            train_classifier()
        except Exception as e:
            print("MIGRATION: Error bootstrapping Naive Bayes model:", e, flush=True)

        first_request_executed = True

@app.before_request
def load_logged_in_user():
    user_id = session.get('user_id')
    if user_id is None:
        g.user = None
    else:
        g.user = db.session.get(User, user_id)

def login_required(view):
    @wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect('/login')
        return view(**kwargs)
    return wrapped_view

# Allowed file check
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in app.config['ALLOWED_EXTENSIONS']

def clean_amount(amount):
    """Clean and round monetary amounts."""
    cleaned_amount = Decimal(amount.replace(',', ''))
    rounded_amount = cleaned_amount.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    return f"{rounded_amount:,.2f}"

def parse_date(date_str):
    """Convert date from DD-MM-YY to DD-MM-YYYY format."""
    return datetime.strptime(date_str, '%d-%m-%y').strftime('%d-%m-%Y')

def clean_particulars(particulars):
    """Clean and structure transaction particulars."""
    # Check if it follows the UPI pattern: UPI/DR or CR/REF/NAME/BANK/UPI_ID/...
    upi_match = re.search(r'UPI/(DR|CR)/(\d+|)//?([^/]+)/([^/]+)/([^/]+)', particulars, re.IGNORECASE)
    if upi_match:
        direction = upi_match.group(1).upper()
        name = upi_match.group(3).strip()
        bank = upi_match.group(4).strip()
        upi_id = upi_match.group(5).strip()
        
        # Clean any trailing dashes/slashes/dots from the fields
        name = re.sub(r'[\s\-.]+$', '', name)
        bank = re.sub(r'[\s\-.]+$', '', bank)
        upi_id = re.sub(r'[\s\-.]+$', '', upi_id)
        
        parts = [direction, name, bank]
        if upi_id:
            parts.append(upi_id)
        return " / ".join(parts)
        
    # Fallback cleaning for non-UPI transactions
    cleaned = re.sub(r'[^\w\s:/\-@#&*(),.]+', '', particulars)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    # Remove trailing noise
    cleaned = re.sub(r'[\s\-.]+$', '', cleaned)
    return cleaned if cleaned else "Unclassified Transaction"

def is_withdrawal(particulars):
    """Determine if a transaction is a withdrawal based on keywords in particulars."""
    p_upper = particulars.upper()
    
    # 1. Direct UPI checks (highly specific)
    if 'UPI/CR/' in p_upper:
        return False
    if 'UPI/DR/' in p_upper:
        return True
        
    # 2. Standalone keywords check
    withdrawal_keywords = ['CHQ RETN', 'TM', 'TRANSFER:', 'RETN', 'INWARD']
    if any(keyword in p_upper for keyword in withdrawal_keywords):
        return True
        
    # 3. Check for Debit marking (DR/Dr) or ACH Debit (ACHDr/ACH DR) using word boundaries
    if re.search(r'\bDR\b|\bACHDR\b', p_upper):
        return True
        
    return False

def process_transaction(date, particulars, grouped_data):
    """Process a single transaction and add it to the grouped data."""
    amounts = re.findall(r'\d{1,5}(?:,\d{3})*\.\d{2}', particulars)
    if amounts:
        amount = clean_amount(amounts[0])
        withdrawal = amount if is_withdrawal(particulars) else '0.00'
        deposit = '0.00' if is_withdrawal(particulars) else amount
        if date not in grouped_data:
            grouped_data[date] = []  # Initialize list for this date
        grouped_data[date].append([date, clean_particulars(particulars), withdrawal, deposit])

def convert_pdf_to_txt(path, csv_path):
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'

    laparams = LAParams(
        all_texts=True, detect_vertical=True,
        line_overlap=0.5, char_margin=1000.0,
        line_margin=2.0, word_margin=2,
        boxes_flow=1
    )
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0  # Process all pages
    caching = True
    pagenos = set()
    grouped_data = {}

    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching, check_extractable=True):
        interpreter.process_page(page)

    text = retstr.getvalue()
    lines = text.split('\n')
    particulars = ""
    date = None
    transaction_start = False

    for line in lines:
        line = line.strip()
        if not line or "Page Total:" in line or "----------" in line:
            continue

        date_match = re.match(r'^(\d{2}-\d{2}-(\d{2}))', line)
        if date_match:
            if transaction_start:
                process_transaction(date, particulars, grouped_data)
                particulars = ""
            transaction_start = True
            full_date = date_match.group(1)
            year_suffix = date_match.group(2)
            date = parse_date(full_date)
            particulars = line.split('-' + year_suffix, 1)[-1].strip()
        else:
            particulars += " " + line.strip()

    if transaction_start:
        process_transaction(date, particulars, grouped_data)

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['DATE', 'PARTICULARS', 'WITHDRAWALS', 'DEPOSITS', 'TRANSACTION COUNT'])
        for date_key, transactions in grouped_data.items():
            # Calculate totals for the day
            total_withdrawal = sum(Decimal(txn[2].replace(',', '')) for txn in transactions if txn[2] != '0.00')
            total_deposit = sum(Decimal(txn[3].replace(',', '')) for txn in transactions if txn[3] != '0.00')
            
            writer.writerow([f"Date: {date_key}", "", "", "", f"Transactions: {len(transactions)}"])
            writer.writerow(['DATE', 'PARTICULARS', 'WITHDRAWALS', 'DEPOSITS'])
            for transaction in transactions:
                writer.writerow(transaction)
            
            # Write totals for the day
            writer.writerow(["", "Total for the day:", f"{total_withdrawal:,.2f}", f"{total_deposit:,.2f}"])
            writer.writerow([])  # Blank row to separate tables
            writer.writerow([])  # Extra blank row 1
            writer.writerow([])  # Extra blank row 2
            writer.writerow([])  # Extra blank row 3

    fp.close()
    device.close()
    retstr.close()
    return text, grouped_data

@app.route('/login')
def login():
    if g.user is not None:
        return redirect('/')
    return render_template('login.html')

@app.route('/create-profile', methods=['POST'])
def create_profile():
    username = request.form.get('username', '').strip()
    if not username:
        flash('Username cannot be empty', 'error')
        return redirect('/login')
        
    unique_id = generate_unique_user_id()
    new_user = User(username=username, unique_id=unique_id)
    db.session.add(new_user)
    db.session.commit()
    
    session['user_id'] = new_user.id
    flash(f'Profile created successfully! Your unique User ID is: {unique_id}. Save this to login from other devices.', 'success')
    return redirect('/')

@app.route('/login-profile', methods=['POST'])
def login_profile():
    unique_id = request.form.get('user_id', '').strip().upper()
    if not unique_id:
        flash('User ID cannot be empty', 'error')
        return redirect('/login')
        
    user = User.query.filter_by(unique_id=unique_id).first()
    if user:
        session['user_id'] = user.id
        flash(f'Welcome back, {user.username}!', 'success')
        return redirect('/')
    else:
        flash('Invalid User ID. Please check and try again.', 'error')
        return redirect('/login')

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect('/login')

@app.route('/')
@login_required
def index():
    recent_files = UploadedFile.query.filter_by(user_id=g.user.id).order_by(UploadedFile.upload_time.desc()).limit(10).all()
    return render_template('upload.html', recent_files=recent_files)

@app.route('/upload', methods=['POST'])
@login_required
def upload_file():
    if 'file' not in request.files:
        flash('No file selected', 'error')
        return redirect('/')

    file = request.files['file']
    if file.filename == '':
        flash('No file selected', 'error')
        return redirect('/')

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        csv_filename = f"{filename}.csv"
        csv_path = os.path.join(app.config['PROCESSED_FOLDER'], csv_filename)
        pdf_text, grouped_data = convert_pdf_to_txt(file_path, csv_path)
        op_bal, cl_bal = extract_balances(pdf_text)
        
        # Save statement metadata to database
        db_file = UploadedFile(
            filename=filename, 
            user_id=g.user.id,
            opening_balance=op_bal,
            closing_balance=cl_bal
        )
        db.session.add(db_file)
        db.session.commit()

        # Save individual transactions to database
        for date_key, transactions in grouped_data.items():
            for tx in transactions:
                particulars = tx[1]
                try:
                    w_val = float(tx[2].replace(',', ''))
                except ValueError:
                    w_val = 0.0
                try:
                    d_val = float(tx[3].replace(',', ''))
                except ValueError:
                    d_val = 0.0
                    
                # Hierarchical Categorization Pipeline
                merchant_key = get_merchant_key(particulars)
                mapping = SavedMapping.query.filter_by(user_id=g.user.id, merchant=merchant_key).first()
                
                if mapping:
                    category = mapping.category
                else:
                    pred_cat, confidence = predict_category(particulars)
                    if pred_cat and confidence >= 0.70:
                        category = pred_cat
                    else:
                        category = categorize_transaction(particulars)
                
                db_tx = Transaction(
                    file_id=db_file.id,
                    date=tx[0],
                    particulars=particulars,
                    category=category,
                    withdrawal=w_val,
                    deposit=d_val,
                    is_manual=False
                )
                db.session.add(db_tx)
        db.session.commit()
        
        # Trigger retraining with new bootstrapped or hard-mapped transactions
        try:
            train_classifier()
        except Exception as e:
            print("ML_UPLOAD: Error training model after upload:", e, flush=True)

        excel_filename = f"{filename}.xlsx"
        excel_path = os.path.join(app.config['PROCESSED_FOLDER'], excel_filename)
        df = pd.read_csv(csv_path)
        df.to_excel(excel_path, index=None, header=True)

        flash('File processed successfully!', 'success')
        return redirect(f'/dashboard/{db_file.id}')

    flash('Invalid file format', 'error')
    return redirect('/')

@app.route('/dashboard/<int:file_id>')
@login_required
def dashboard(file_id):
    file = UploadedFile.query.get_or_404(file_id)
    if file.user_id != g.user.id:
        flash('Unauthorized access.', 'error')
        return redirect('/')
        
    recent_files = UploadedFile.query.filter_by(user_id=g.user.id).order_by(UploadedFile.upload_time.desc()).limit(10).all()
    excel_filename = f"{file.filename}.xlsx"
    return render_template('dashboard.html', file=file, recent_files=recent_files, excel_filename=excel_filename)

@app.route('/api/dashboard-data/<int:file_id>')
@login_required
def api_dashboard_data(file_id):
    file = UploadedFile.query.get_or_404(file_id)
    if file.user_id != g.user.id:
        return jsonify({'error': 'Unauthorized'}), 403
        
    transactions = Transaction.query.filter_by(file_id=file_id).all()
    
    total_withdrawals = 0.0
    total_deposits = 0.0
    category_totals = {}
    category_counts = {}
    daily_trends = {}
    
    tx_list = []
    for tx in transactions:
        total_withdrawals += tx.withdrawal
        total_deposits += tx.deposit
        
        # Spent analysis (Withdrawals only)
        if tx.withdrawal > 0:
            category_totals[tx.category] = category_totals.get(tx.category, 0.0) + tx.withdrawal
            
        # Count transactions per category
        category_counts[tx.category] = category_counts.get(tx.category, 0) + 1
        
        # Daily trends
        if tx.date not in daily_trends:
            daily_trends[tx.date] = {'withdrawal': 0.0, 'deposit': 0.0}
        daily_trends[tx.date]['withdrawal'] += tx.withdrawal
        daily_trends[tx.date]['deposit'] += tx.deposit
        
        tx_list.append({
            'id': tx.id,
            'date': tx.date,
            'particulars': tx.particulars,
            'category': tx.category,
            'withdrawal': tx.withdrawal,
            'deposit': tx.deposit
        })
        
    # Sort trends chronologically
    sorted_dates = sorted(daily_trends.keys(), key=lambda d: datetime.strptime(d, '%d-%m-%Y'))
    trend_labels = sorted_dates
    trend_withdrawals = [daily_trends[d]['withdrawal'] for d in sorted_dates]
    trend_deposits = [daily_trends[d]['deposit'] for d in sorted_dates]
    
    return jsonify({
        'filename': file.filename,
        'upload_time': file.upload_time.strftime('%Y-%m-%d %H:%M:%S') if file.upload_time else '',
        'total_withdrawals': round(total_withdrawals, 2),
        'total_deposits': round(total_deposits, 2),
        'net_savings': round(total_deposits - total_withdrawals, 2),
        'transaction_count': len(transactions),
        'opening_balance': round(file.opening_balance, 2) if file.opening_balance is not None else 0.0,
        'closing_balance': round(file.closing_balance, 2) if file.closing_balance is not None else 0.0,
        'category_totals': {k: round(v, 2) for k, v in category_totals.items()},
        'category_counts': category_counts,
        'daily_trends': {
            'labels': trend_labels,
            'withdrawals': trend_withdrawals,
            'deposits': trend_deposits
        },
        'transactions': tx_list
    })

@app.route('/api/update-category', methods=['POST'])
@login_required
def update_category():
    data = request.get_json() or {}
    tx_id = data.get('transaction_id')
    new_category = data.get('category')
    
    if not tx_id or not new_category:
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400
        
    tx = Transaction.query.get(tx_id)
    if not tx:
        return jsonify({'success': False, 'error': 'Transaction not found'}), 404
        
    file = UploadedFile.query.get(tx.file_id)
    if file.user_id != g.user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
    tx.category = new_category
    tx.is_manual = True
    
    # Upsert custom hard mapping for this merchant key under user profile
    merchant_key = get_merchant_key(tx.particulars)
    mapping = SavedMapping.query.filter_by(user_id=g.user.id, merchant=merchant_key).first()
    if mapping:
        mapping.category = new_category
    else:
        mapping = SavedMapping(user_id=g.user.id, merchant=merchant_key, category=new_category)
        db.session.add(mapping)
        
    db.session.commit()
    
    # Retrain ML model with new data
    try:
        train_classifier()
    except Exception as e:
        print("ML_ROUTE: Error retraining model after manual update:", e, flush=True)
        
    return jsonify({'success': True})

@app.route('/api/swap-transaction-amount', methods=['POST'])
@login_required
def swap_transaction_amount():
    data = request.get_json() or {}
    tx_id = data.get('transaction_id')
    
    if not tx_id:
        return jsonify({'success': False, 'error': 'Missing transaction_id'}), 400
        
    tx = Transaction.query.get(tx_id)
    if not tx:
        return jsonify({'success': False, 'error': 'Transaction not found'}), 404
        
    file = UploadedFile.query.get(tx.file_id)
    if file.user_id != g.user.id:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
    # Swap withdrawal and deposit
    tx.withdrawal, tx.deposit = tx.deposit, tx.withdrawal
    db.session.commit()
    
    return jsonify({'success': True})

@app.route('/delete-statement/<int:file_id>', methods=['POST'])
@login_required
def delete_statement(file_id):
    file = UploadedFile.query.get_or_404(file_id)
    if file.user_id != g.user.id:
        flash('Unauthorized action.', 'error')
        return redirect('/')
    
    # Delete local files
    upload_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    if os.path.exists(upload_path):
        try:
            os.remove(upload_path)
        except Exception:
            pass
            
    csv_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{file.filename}.csv")
    if os.path.exists(csv_path):
        try:
            os.remove(csv_path)
        except Exception:
            pass
            
    excel_path = os.path.join(app.config['PROCESSED_FOLDER'], f"{file.filename}.xlsx")
    if os.path.exists(excel_path):
        try:
            os.remove(excel_path)
        except Exception:
            pass
            
    db.session.delete(file)
    db.session.commit()
    flash('Statement deleted successfully!', 'success')
    return redirect('/')

@app.route('/download/<filename>')
@login_required
def download_file(filename):
    # Retrieve file entry to verify ownership
    # The filename matches the output excel, which is secure_filename(pdf_name) + ".xlsx"
    orig_pdf_name = filename.rsplit('.', 1)[0]
    file_record = UploadedFile.query.filter_by(filename=orig_pdf_name, user_id=g.user.id).first()
    if not file_record:
        # Fallback search inside the user's files
        user_files = UploadedFile.query.filter_by(user_id=g.user.id).all()
        has_access = any(f"{uf.filename}.xlsx" == filename for uf in user_files)
        if not has_access:
            flash('Access to this download is restricted.', 'error')
            return redirect('/')
            
    file_path = os.path.join(app.config['PROCESSED_FOLDER'], filename)
    return send_file(file_path, as_attachment=True)

@app.route('/debug-text/<int:file_id>')
@login_required
def debug_text(file_id):
    file = UploadedFile.query.get_or_404(file_id)
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
    
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(file_path, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    for page in PDFPage.get_pages(fp):
        interpreter.process_page(page)
    text = retstr.getvalue()
    fp.close()
    device.close()
    retstr.close()
    
    lines = text.split('\n')
    output_lines = []
    
    # 1. Print lines around opening balance (known to be around 288)
    output_lines.append("=== LINES 270-320 ===")
    for idx in range(max(0, 270), min(len(lines), 320)):
        output_lines.append(f"{idx}: {lines[idx]}")
        
    # 2. Print lines around closing balance
    output_lines.append("\n=== LINES WITH CLOSING BALANCE AND SURROUNDINGS ===")
    for idx, line in enumerate(lines):
        if "closing balance" in line.lower():
            output_lines.append(f"\nFound closing balance at line {idx}:")
            for offset in range(-5, 10):
                target_idx = idx + offset
                if 0 <= target_idx < len(lines):
                    output_lines.append(f"{target_idx}: {lines[target_idx]}")
                    
    # 3. Print lines containing 'balance'
    output_lines.append("\n=== ALL LINES WITH 'BALANCE' ===")
    for idx, line in enumerate(lines):
        if "balance" in line.lower():
            output_lines.append(f"{idx}: {line}")
            
    return "<pre>" + "\n".join(output_lines) + "</pre>"

if __name__ == '__main__':
    app.run(debug=True, port=5000)
