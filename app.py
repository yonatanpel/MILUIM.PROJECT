import streamlit as st
import pandas as pd
import time
import base64
import os
from datetime import datetime, timedelta

# --- הגדרות תצורה ---
st.set_page_config(page_title="MiluiMate - מערכת שיבוץ חכמה", layout="centered")

# --- פונקציית רקע ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# --- פונקציות עזר ---
def show_logo():
    st.markdown("<h1>🐌 MiluiMate</h1>", unsafe_allow_html=True)

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

# --- אתחול דאטא ---
if 'db_soldiers' not in st.session_state:
    db = {}
    names_list = ["אבי כהן", "בני לוי", "גדי מזרחי", "דוד שוורץ", "הראל לוין", "וואליד פרץ", "זיו דויד", "חגי אברהם", "טום אהרון", "יניב סגל", "כפיר חדד", "ליאור מנצור", "משה אטיאס", "ניסים כץ", "סמי רז", "עודד אלבז", "פז בנאי", "צבי דהן", "קובי גולד", "רונן חג'ג'", "שמעון נחמיאס", "תמיר מלכה", "אופיר יוסף", "בוזי צדיק", "גולן ברק", "דורון פלד", "חן גל", "יואב ששון", "מיקי עמר", "נאור וקנין", "אסף לביא", "בר גולן", "דני רוזן", "לוי שפירא", "שי יפת", "רמי ארזי", "אלי שמש", "אלכס מוסקוביץ", "תומר דנינו", "שרון בן דוד", "אריק כדורי", "דני בוחבוט", "זאב שבתאי", "ירון חסיד", "מנחם דיין", "נדב זקן", "סער מור", "עמי גבאי", "צחי פינטו", "קרי תורג'מן", "רוני לוי", "שקד אלימלך", "תום גרוס", "אילן מלכא", "בוריס וקנין", "גיל סעדה", "דני ברוך", "הראל יצחק", "וובה חלבי", "זיו אלקבץ"]
    roles_pool = ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"]
    
    soldier_idx = 1
    for dept in [1, 2, 3]:
        for i in range(1, 21):
            s_name = names_list[(soldier_idx-1) % len(names_list)]
            s_role = roles_pool[(soldier_idx - 1) % len(roles_pool)]
            db[s_name] = {"role": s_role, "department": dept, "constraints": [{"סוג האילוץ": "אין לי העדפה", "סטטוס": "אושר"}]}
            soldier_idx += 1
    st.session_state['db_soldiers'] = db

if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {"mefaked": {"pass": "1234", "role": "commander", "name": "מפקד מחלקה"}}

# --- לוגיקה פשוטה למסכים ---
def main():
    if 'logged_in' not in st.session_state: st.session_state['logged_in'] = False
    
    if not st.session_state['logged_in']:
        st.markdown("<h1>MiluiMate - כניסה</h1>", unsafe_allow_html=True)
        u = st.text_input("שם משתמש")
        p = st.text_input("סיסמה", type="password")
        if st.button("התחבר"):
            if u in st.session_state['users_db'] and st.session_state['users_db'][u]["pass"] == p:
                st.session_state['logged_in'] = True
                st.rerun()
    else:
        st.write("ברוך הבא למערכת")
        if st.button("התנתק"):
            st.session_state['logged_in'] = False
            st.rerun()

if __name__ == "__main__":
    main()
