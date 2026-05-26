import streamlit as st
import pandas as pd
import time
from datetime import datetime, timedelta

st.set_page_config(page_title="MiluiMate - מערכת שיבוץ", layout="wide")

# --- CSS עיצוב ---
st.markdown("""
    <style>
    html, body, .stApp { direction: rtl !important; text-align: right !important; font-family: 'Assistant', sans-serif; }
    h1 { text-align: center !important; }
    .stButton>button { background-color: #556644; color: white; width: 100%; border-radius: 8px; }
    </style>
""", unsafe_allow_html=True)

# --- אתחול דאטא (60 שמות) ---
if 'db_soldiers' not in st.session_state:
    names_list = ["אבי כהן", "בני לוי", "גדי מזרחי", "דוד שוורץ", "הראל לוין", "וואליד פרץ", "זיו דויד", "חגי אברהם", "טום אהרון", "יניב סגל", "כפיר חדד", "ליאור מנצור", "משה אטיאס", "ניסים כץ", "סמי רז", "עודד אלבז", "פז בנאי", "צבי דהן", "קובי גולד", "רונן חג'ג'", "שמעון נחמיאס", "תמיר מלכה", "אופיר יוסף", "בוזי צדיק", "גולן ברק", "דורון פלד", "חן גל", "יואב ששון", "מיקי עמר", "נאור וקנין", "אסף לביא", "בר גולן", "דני רוזן", "לוי שפירא", "שי יפת", "רמי ארזי", "אלי שמש", "אלכס מוסקוביץ", "תומר דנינו", "שרון בן דוד", "אריק כדורי", "דני בוחבוט", "זאב שבתאי", "ירון חסיד", "מנחם דיין", "נדב זקן", "סער מור", "עמי גבאי", "צחי פינטו", "קרי תורג'מן", "רוני לוי", "שיר אלימלך", "תום גרוס", "אילן מלכא", "בוריס וקנין", "גיל סעדה", "דני ברוך", "הראל יצחק", "וובה חלבי", "זיו אלקבץ"]
    roles = ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"]
    db = {}
    for idx, name in enumerate(names_list):
        db[name] = {"role": roles[idx % len(roles)], "department": (idx // 20) + 1, "constraints": [{"סוג האילוץ": "אין לי העדפה", "סטטוס": "אושר"}]}
    st.session_state['db_soldiers'] = db

if 'dept_schedules' not in st.session_state: st.session_state['dept_schedules'] = {}
if 'users_db' not in st.session_state: st.session_state['users_db'] = {"mefaked": {"pass": "1234", "role": "commander", "name": "סרן דוד"}}

# --- פונקציות מסכים ---
def commander_page():
    st.markdown("<h1>ניהול שיבוץ פלוגתי</h1>", unsafe_allow_html=True)
    dept = st.selectbox("בחר מחלקה:", [1,2,3])
    
    t1, t2 = st.tabs(["🚦 סטטוס אילוצים", "📅 לוח שיבוץ"])
    
    with t1:
        rows = [{"שם החייל": n, **d.get("constraints", [{}])[0]} for n, d in st.session_state['db_soldiers'].items() if d.get("department") == dept]
        df = pd.DataFrame(rows)
        df.insert(0, 'מס"ד', range(1, len(df)+1))
        st.dataframe(df, hide_index=True, use_container_width=True)

    with t2:
        if st.button("אתחל לוח שיבוץ"):
            data = {"שם החייל": [n for n, d in st.session_state['db_soldiers'].items() if d.get("department") == dept]}
            for day in ["יום א'", "יום ב'", "יום ג'", "יום ד'", "יום ה'"]:
                data[day] = "נוכח בבסיס"
            st.session_state['dept_schedules'][dept] = pd.DataFrame(data)
            st.rerun()
            
        if dept in st.session_state['dept_schedules']:
            df = st.session_state['dept_schedules'][dept]
            # הגדרת צבעים דינמיים לפי ערך התא
            st.data_editor(
                df,
                column_config={
                    "יום א'": st.column_config.SelectboxColumn(options=["נוכח בבסיס", "בבית (חופשה)"]),
                    "יום ב'": st.column_config.SelectboxColumn(options=["נוכח בבסיס", "בבית (חופשה)"]),
                    "יום ג'": st.column_config.SelectboxColumn(options=["נוכח בבסיס", "בבית (חופשה)"]),
                    "יום ד'": st.column_config.SelectboxColumn(options=["נוכח בבסיס", "בבית (חופשה)"]),
                    "יום ה'": st.column_config.SelectboxColumn(options=["נוכח בבסיס", "בבית (חופשה)"]),
                },
                use_container_width=True
            )

    if st.button("התנתק"): st.session_state.update({'logged_in': False}); st.rerun()

# --- ניתוב ---
if not st.session_state.get('logged_in'):
    with st.form("login"):
        u = st.text_input("שם משתמש")
        p = st.text_input("סיסמה", type="password")
        if st.form_submit_button("התחבר"):
            if u in st.session_state['users_db']:
                st.session_state.update({'logged_in': True, 'user_info': st.session_state['users_db'][u]}); st.rerun()
else:
    commander_page()
