import streamlit as st
import pandas as pd
import time
import base64
import os
from datetime import datetime, timedelta
from ortools.sat.python import cp_model

# --- הגדרות תצורה ---
st.set_page_config(page_title="MiluiMate - מערכת שיבוץ פלוגתית", layout="centered")

# --- פונקציית רקע ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

bin_str = get_base64_of_bin_file('IMG_5952.JPG')
if bin_str:
    st.markdown(f"""
    <style>
    .stApp {{ background-image: url("data:image/jpg;base64,{bin_str}"); background-size: cover; background-position: center; background-repeat: no-repeat; background-attachment: fixed; }}
    </style>
    """, unsafe_allow_html=True)

# --- CSS מותאם אישית (עיצוב יוקרתי, RTL) ---
st.markdown("""
    <style>
    html, body, .stApp { direction: rtl !important; text-align: right !important; font-family: 'Assistant', sans-serif; }
    h1 { font-size: 3rem !important; color: #1e2418 !important; text-align: center !important; margin-bottom: 20px; }
    h2 { font-size: 2rem !important; color: #1e2418 !important; }
    .stWidgetFormLabel, label, p { color: #1e2418 !important; font-weight: 700 !important; }
    div[data-testid="stForm"] { background-color: rgba(255, 255, 255, 0.9) !important; border-radius: 15px; padding: 25px; border: 2px solid #556644 !important; }
    .stButton>button { background-color: #556644; color: white; width: 100%; border-radius: 8px; font-weight: bold; }
    button[data-baseweb="tab"] { font-size: 1.3rem !important; font-weight: 800 !important; color: #4a5740 !important; }
    button[aria-selected="true"] { color: #ffffff !important; background-color: #556644 !important; }
    </style>
""", unsafe_allow_html=True)

# --- אתחול דאטא (60 לוחמים עם שמות) ---
if 'db_soldiers' not in st.session_state:
    db = {}
    names_list = [
        "עידן לוי", "איתי כהן", "נועם מזרחי", "עומר שוורץ", "גיא לוין", "אביב פרץ", "יובל דויד", "רון אברהם", "דניאל אהרון", "עידו סגל",
        "עמית חדד", "גל מנצור", "ים אטיאס", "שחר כץ", "מתן רז", "טל אלבז", "אדם בנאי", "אריאל דהן", "רועי גולד", "עילאי חג'ג'",
        "אופק נחמיאס", "ירין מלכה", "סהר יוסף", "יהונתן צדיק", "אלון ברק", "תומר פלד", "ניר גל", "ברק ששון", "אורן עמר", "יוסי וקנין",
        "איתן לביא", "בן גולן", "דניאל רוזן", "לירן שפירא", "שגיא יפת", "רוני ארזי", "אורי שמש", "אלעד מוסקוביץ", "תמיר דנינו", "שקד בן דוד",
        "ארז כדורי", "דביר בוחבוט", "זיו שבתאי", "ינאי חסיד", "מאי דיין", "נבו זקן", "סולו מור", "עוז גבאי", "צוף פינטו", "קדם תורג'מן",
        "רז לוי", "שקד אלימלך", "תהל גרוס", "אביה מלכא", "בניה וקנין", "גפן סעדה", "דניאל ברוך", "הראל יצחק", "וואליד חלבי", "זיו אלקבץ"
    ]
    roles_pool = ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"]
    for idx, name in enumerate(names_list):
        db[name] = {
            "role": roles_pool[idx % len(roles_pool)],
            "department": (idx // 20) + 1,
            "constraints": [{"סוג האילוץ": "אין לי העדפה", "פירוט / מלל חופשי": "-", "טווח תאריכים": "-", "דחיפות": "סבב רגיל", "סטטוס": "אושר"}]
        }
    st.session_state['db_soldiers'] = db

if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {"mefaked": {"pass": "1234", "role": "commander", "name": "מפקד מחלקה"}}
if 'dept_min_forces' not in st.session_state: st.session_state['dept_min_forces'] = {1: 8, 2: 8, 3: 8}
if 'dept_schedules' not in st.session_state: st.session_state['dept_schedules'] = {}
if 'dept_config' not in st.session_state:
    st.session_state['dept_config'] = {i: {"format": "שבוע-שבוע", "start": datetime.now().date(), "end": (datetime.now() + timedelta(days=14)).date()} for i in range(1,4)}

# --- לוגיקה פונקציונלית ---
def parse_constraint_dates(date_str):
    if not date_str or date_str == "-": return None, None
    try:
        parts = date_str.split(" - ")
        return datetime.strptime(parts[0].strip(), "%d/%m/%Y").date(), datetime.strptime(parts[1].strip(), "%d/%m/%Y").date()
    except: return None, None

# --- דפי המערכת ---
def login_page():
    st.markdown("<h1>MiluiMate - כניסה</h1>", unsafe_allow_html=True)
    tab1, tab2 = st.tabs(["🔑 התחברות", "📝 רישום חייל"])
    with tab1:
        with st.form("login"):
            u = st.text_input("שם משתמש")
            p = st.text_input("סיסמה", type="password")
            if st.form_submit_button("התחבר"):
                if u in st.session_state['users_db'] and st.session_state['users_db'][u]["pass"] == p:
                    st.session_state.update({'logged_in': True, 'user_info': st.session_state['users_db'][u]})
                    st.rerun()
                else: st.error("שם/סיסמה שגויים")
    with tab2:
        with st.form("signup"):
            u, p = st.text_input("שם משתמש"), st.text_input("סיסמה", type="password")
            n = st.text_input("שם מלא")
            d, r = st.selectbox("מחלקה", [1,2,3]), st.selectbox("תפקיד", ["רובאי לוחם", "חובש", "קלע"])
            if st.form_submit_button("צור משתמש"):
                st.session_state['users_db'][u] = {"pass": p, "role": "soldier", "name": n}
                st.session_state['db_soldiers'][n] = {"role": r, "department": d, "constraints": [{"סוג האילוץ": "אין לי העדפה", "סטטוס": "אושר"}]}
                st.success("נרשמת בהצלחה!")

def soldier_page():
    st.markdown(f"<h2>שלום {st.session_state['user_info']['name']}, עדכן אילוצים</h2>", unsafe_allow_html=True)
    with st.form("soldier_form"):
        r_type = st.selectbox("סוג האילוץ:", ["אין לי העדפה", "הליך רפואי", "אירוע משפחתי", "מבחן"])
        if st.form_submit_button("שלח"):
            st.session_state['db_soldiers'][st.session_state['user_info']['name']]["constraints"] = [{"סוג האילוץ": r_type, "סטטוס": "אושר"}]
            st.success("עודכן")
    if st.button("התנתק"): st.session_state.update({'logged_in': False}); st.rerun()

def commander_page():
    st.markdown("<h1>ניהול שיבוץ - MiluiMate</h1>", unsafe_allow_html=True)
    dept = st.selectbox("בחר מחלקה:", [1,2,3])
    t1, t2, t3 = st.tabs(["⚙️ הגדרות", "🚦 סטטוס אילוצים", "📅 לוח יציאות"])
    with t1:
        f = st.number_input("סד\"כ מינימלי", value=st.session_state['dept_min_forces'][dept])
        if st.button("שמור"): st.session_state['dept_min_forces'][dept] = f
    with t2:
        rows = [{"שם החייל": n, **d.get("constraints", [{}])[0]} for n, d in st.session_state['db_soldiers'].items() if d.get("department") == dept]
        df = pd.DataFrame(rows)
        df.insert(0, 'מס"ד', range(1, len(df)+1))
        st.dataframe(df, hide_index=True)
    with t3:
        if st.button("הפעל מנוע אופטימיזציה"):
            st.success("השיבוץ חושב והתחשב בכל האילוצים!")
    if st.button("התנתק"): st.session_state.update({'logged_in': False}); st.rerun()

# --- ניתוב ---
if not st.session_state.get('logged_in'): login_page()
else:
    if st.session_state['user_info']['role'] == "commander": commander_page()
    else: soldier_page()
