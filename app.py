import streamlit as st
import pandas as pd
import time
import base64
import os
from datetime import datetime, timedelta
from ortools.sat.python import cp_model

# --- הגדרות תצורה בסיסיות לעמוד ---
st.set_page_config(page_title="MiluiMate - מערכת שיבוץ חכמה", layout="centered")

# --- פונקציה להמרת תמונת הרקע המקומית ל-Base64 ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

bin_str = get_base64_of_bin_file('IMG_5952.JPG')
if bin_str:
    background_css = f"""
    <style>
    .stApp {{
        background-image: url("data:image/jpg;base64,{bin_str}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """
    st.markdown(background_css, unsafe_allow_html=True)
else:
    st.markdown("""
        <style>
        .stApp { background-color: #e6e5df; }
        </style>
    """, unsafe_allow_html=True)

# --- הזרקת CSS מותאם אישית - יישור, פונטים וטבלאות ---
st.markdown("""
    <style>
    html, body, [class*="css"], .stApp  {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Assistant', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stWidgetFormLabel, label, [data-testid="stWidgetLabel"] p, .stMarkdown p {
        text-align: right !important;
        direction: rtl !important;
        color: #1e2418 !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        margin-bottom: 8px;
    }
    
    h1 {
        font-size: 3.2rem !important;
        color: #1e2418 !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin-bottom: 30px;
    }
    
    h2 {
        font-size: 2.2rem !important;
        color: #1e2418 !important;
        font-weight: 700 !important;
        margin-top: 15px;
        text-align: right !important;
    }
    
    div[data-testid="stForm"] h3 {
        text-align: center !important;
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stDateInput>div>div>input {
        background-color: #ffffff !important;
        color: #1e2418 !important;
        border: 2px solid #556644 !important;
        border-radius: 8px !important;
        font-size: 1.2rem !important;
        padding: 8px !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2.4rem !important;
        font-weight: bold !important;
        color: #1e2418 !important;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.94);
        border: 2px solid #556644;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 6px 18px rgba(0, 0, 0, 0.08);
    }
    
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.92) !important;
        border-radius: 16px;
        padding: 35px;
        border: 2px solid #556644 !important;
        box-shadow: 0 12px 45px rgba(0,0,0,0.1);
    }
    
    .stButton>button {
        background-color: #556644;
        color: white;
        border-radius: 8px;
        border: 1px solid #3d4a31;
        padding: 14px 35px;
        font-size: 1.3rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #3d4a31;
        transform: translateY(-2px);
    }
    
    button[data-baseweb="tab"] {
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        color: #4a5740 !important;
        padding: 14px 35px !important;
        background-color: rgba(255, 255, 255, 0.6) !important;
        border-radius: 10px 10px 0 0 !important;
        margin-left: 10px !important;
        border: 2px solid rgba(85, 102, 68, 0.2) !important;
        border-bottom: none !important;
        transition: all 0.2s ease;
    }
    
    button[aria-selected="true"] {
        color: #ffffff !important;
        background-color: #556644 !important;
        border-color: #556644 !important;
        box-shadow: 0px -4px 15px rgba(0,0,0,0.12);
    }
    
    .stDataFrame, [data-testid="stDataEditor"] {
        background-color: rgba(255, 255, 255, 0.96) !important;
        border-radius: 12px;
        padding: 8px;
        border: 2px solid #556644;
    }
    
    [data-testid="stImage"] {
        mix-blend-mode: multiply;
    }
    .stAlert {
        border-radius: 10px;
        direction: rtl;
    }
    </style>
""", unsafe_allow_html=True)

# --- פונקציות עזר ופונקציית לוגיקת תאריכים ---
def show_logo():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        possible_names = ["logo.jpeg", "logo.jpg", "logo.png", "LOGO.jpeg", "LOGO.JPG", "LOGO.PNG", "Logo.jpeg", "Logo.jpg"]
        logo_found = False
        for name in possible_names:
            if os.path.exists(name):
                try:
                    st.image(name, use_container_width=True)
                    logo_found = True
                    break
                except:
                    pass
        if not logo_found:
            st.markdown("<h1>🐌 MiluiMate</h1>", unsafe_allow_html=True)

# ממיר מחרוזת של טווח תאריכים ("DD/MM/YYYY - DD/MM/YYYY") לאובייקטי datetime
def parse_constraint_dates(date_str):
    if not date_str or date_str == "-" or " - " not in date_str:
        return None, None
    try:
        parts = date_str.split(" - ")
        start_d = datetime.strptime(parts[0].strip(), "%d/%m/%Y").date()
        end_d = datetime.strptime(parts[1].strip(), "%d/%m/%Y").date()
        return start_d, end_d
    except:
        return None, None

# פונקציית צביעה ייעודית לטבלת השיבוצים (מסך 3)
def color_schedule(val):
    if isinstance(val, str):
        if "בבית (חופשה)" in val:
            return 'background-color: #c3e6cb; color: #155724; font-weight: bold;' # ירוק
        elif "נוכח בבסיס" in val:
            return 'background-color: #f5c6cb; color: #721c24;' # אדום/ורוד
        elif "יציאה קצרה" in val:
            return 'background-color: #ffeeba; color: #856404;' # צהוב
        elif "הארכת שהות" in val:
            return 'background-color: #bee5eb; color: #0c5460;' # תכלת
    return ''

# --- אתחול בסיס נתונים ---
if 'db_soldiers' not in st.session_state:
    db = {}
    roles_pool = ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"]
    
    soldier_idx = 1
    for dept in [1, 2, 3]:
        for i in range(1, 21):
            s_name = f"לוחם {soldier_idx}"
            s_role = roles_pool[(soldier_idx - 1) % len(roles_pool)]
            
            constraints = []
            if soldier_idx == 3:
                constraints.append({"סוג האילוץ": "הליך רפואי", "פירוט / מלל חופשי": "ביקור רופא מומחה", "טווח תאריכים": (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y") + " - " + (datetime.now() + timedelta(days=4)).strftime("%d/%m/%Y"), "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"})
            elif soldier_idx == 24:
                constraints.append({"סוג האילוץ": "מבחן/לימודים", "פירוט / מלל חופשי": "מבחן סמסטר", "טווח תאריכים": (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y") + " - " + (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"), "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"})
            else:
                constraints.append({"סוג האילוץ": "אין לי העדפה", "פירוט / מלל חופשי": "זמין לסבב מחלקתי הוגן", "טווח תאריכים": "-", "דחיפות": "סבב רגיל", "סטטוס": "אושר"})
                
            db[s_name] = {
                "role": s_role,
                "department": dept,
                "constraints": constraints
            }
            soldier_idx += 1
            
    st.session_state['db_soldiers'] = db

if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "mefaked": {"pass": "1234", "role": "commander", "name": "מפקד מחלקה"},
        "hayal1": {"pass": "0000", "role": "soldier", "name": "לוחם 3"},
    }

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None
if 'dept_min_forces' not in st.session_state:
    st.session_state['dept_min_forces'] = {1: 8, 2: 8, 3: 8} # עדכנתי מינימום ל-8 מתוך 20
if 'dept_schedules' not in st.session_state:
    st.session_state['dept_schedules'] = {}
if 'dept_config' not in st.session_state:
    st.session_state['dept_config'] = {
        1: {"format": "שבוע-שבוע", "start": datetime.now().date(), "end": (datetime.now() + timedelta(days=14)).date()},
        2: {"format": "חמשו\"ש", "start": datetime.now().date(), "end": (datetime.now() + timedelta(days=14)).date()},
        3: {"format": "שבוע-שבוע", "start": datetime.now().date(), "end": (datetime.now() + timedelta(days=14)).date()},
    }

def authenticate(username, password):
    users = st.session_state['users_db']
    if username in users and users[username]["pass"] == password:
        return users[username]
    return None

# --- מסך 1: התחברות והרשמה ---
def login_page():
    show_logo()
    st.markdown("<h1>MiluiMate - כניסה למערכת</h1>", unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["🔑 התחברות למערכת", "📝 יצירת משתמש חדש"])
    
    with tab_login:
        with st.form("login_form"):
            st.markdown("### התחברות משתמש קיים")
            username = st.text_input("שם משתמש:")
            password = st.text_input("סיסמה:", type="password")
            submit = st.form_submit_button("התחבר למערכת")
            
            if submit:
                user = authenticate(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = user
                    st.rerun()
                else:
                    st.error("שם משתמש או סיסמה שגויים.")

    with tab_signup:
        with st.form("signup_form"):
            st.markdown("### רישום חייל חדש לפלוגה")
            new_username = st.text_input("בחר שם משתמש (באנגלית/מספרים לכניסה עתידית):")
            new_password = st.text_input("בחר סיסמה:", type="password")
            new_name = st.text_input("שם מלא (כפי שיופיע למפקד בטבלאות):")
            
            col_dept, col_role = st.columns(2)
            with col_dept:
                new_dept = st.selectbox("שיוך למחלקה:", [1, 2, 3])
            with col_role:
                new_role = st.selectbox("תפקיד / פק\"ל:", ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"])
            
            submit_signup = st.form_submit_button("➕ צור משתמש והתחבר אוטומטית")
            
            if submit_signup:
                if new_username in st.session_state['users_db']:
                    st.error("שם המשתמש כבר תפוס במערכת. אנא בחר שם משתמש אחר.")
                elif not new_username or not new_password or not new_name:
                    st.error("אנא מלא את כל השדות.")
                else:
                    st.session_state['users_db'][new_username] = {"pass": new_password, "role": "soldier", "name": new_name}
                    st.session_state['db_soldiers'][new_name] = {
                        "role": new_role, "department": new_dept,
                        "constraints": [{"סוג האילוץ": "אין לי העדפה", "פירוט / מלל חופשי": "זמין לסבב מחלקתי הוגן", "טווח תאריכים": "-", "דחיפות": "סבב רגיל", "סטטוס": "אושר"}]
                    }
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = st.session_state['users_db'][new_username]
                    st.rerun()

# --- מסך 2: ממשק חייל ---
def soldier_page():
    show_
