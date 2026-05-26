import streamlit as st
import pandas as pd
import time
import base64
import os
from datetime import datetime, timedelta
from ortools.sat.python import cp_model

# --- הגדרות תצורה בסיסיות לעמוד ---
st.set_page_config(page_title="MiluiMate - מערכת פיקוד ושליטה", layout="centered")

# --- פונקציה להמרת תמונת הרקע המקומית ל-Base64 ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

# ניסיון טעינת רקע ההסוואה שהעלית
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

# --- הזרקת CSS מותאם אישית לעיצוב חמ"ל יוקרתי, קריא ובעל פונטים מוגדלים ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        font-family: 'Assistant', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* הגדלת כותרות ראשיות */
    h1 {
        font-size: 3rem !important;
        color: #1e2418 !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 10px;
    }
    h2 {
        font-size: 2.2rem !important;
        color: #1e2418 !important;
        font-weight: 700 !important;
        margin-top: 15px;
    }
    h3 {
        font-size: 1.6rem !important;
        color: #2e3b23 !important;
        font-weight: 600 !important;
    }
    
    /* הגדלת תוויות ותפריטים */
    .stWidgetFormLabel, label, [data-testid="stWidgetLabel"] p {
        color: #1e2418 !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        margin-bottom: 6px;
    }
    
    /* שדות קלט לבנים ונקיים */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #1e2418 !important;
        border: 2px solid #556644 !important;
        border-radius: 6px !important;
        font-size: 1.1rem !important;
    }
    
    /* כרטיסיות מדדים מודגשות */
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: bold !important;
        color: #1e2418 !important;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.9);
        border: 2px solid #556644;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.12);
    }
    
    /* עיצוב טפסים */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.88) !important;
        border-radius: 14px;
        padding: 25px;
        border: 2px solid #556644 !important;
        box-shadow: 0 10px 35px rgba(0,0,0,0.12);
    }
    
    /* כפתורים מבצעיים מוגדלים */
    .stButton>button {
        background-color: #556644;
        color: white;
        border-radius: 8px;
        border: 1px solid #3d4a31;
        padding: 12px 28px;
        font-size: 1.2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.15);
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #3d4a31;
        color: #ffffff;
        transform: translateY(-2px);
    }
    
    /* עיצוב לשוניות המפקד (Tabs) - פונט גדול ובולט */
    button[data-baseweb="tab"] {
        font-size: 1.3rem !important;
        font-weight: bold !important;
        color: #4a5740 !important;
        padding: 12px 20px !important;
    }
    button[aria-selected="true"] {
        color: #1e2418 !important;
        border-bottom-color: #1e2418 !important;
        background-color: rgba(255, 255, 255, 0.4) !important;
        border-radius: 8px 8px 0 0;
    }
    
    /* עיצוב טבלאות השיבוץ המעוצבות */
    .stDataFrame, [data-testid="stDataEditor"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px;
        padding: 5px;
        border: 1px solid #556644;
    }
    
    [data-testid="stImage"] {
        mix-blend-mode: multiply;
    }
    .stAlert {
        border-radius: 8px;
        direction: rtl;
    }
    </style>
""", unsafe_allow_html=True)

# --- פונקציות עזר ---
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

# --- אתחול מסד נתונים וירטואלי משותף (לסנכרון בזמן אמת עם דחיפויות) ---
if 'db_soldiers' not in st.session_state:
    st.session_state['db_soldiers'] = {
        "רועי": {"role": "חובש", "constraints": [{"סוג": "הליך רפואי", "פירוט": "ניתוח כירורגי באסותא", "טווח": "27/05/2026 - 29/05/2026", "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"}]},
        "דניאל": {"role": "נגביסט", "constraints": []},
        "יוסי": {"role": "מפקד כיתה", "constraints": [{"סוג": "מבחן/לימודים", "פירוט": "מבחן מועד א' בכלכלה מאקרו", "טווח": "26/05/2026 - 26/05/2026", "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"}]},
        "אביב": {"role": "קלע", "constraints": [{"סוג": "אירוע משפחתי", "פירוט": "חתונה של אחותי", "טווח": "28/05/2026 - 28/05/2026", "דחיפות": "דרגה ב' - בינוני", "סטטוס": "בבדיקה"}]},
        "איתי": {"role": "נהג", "constraints": []},
        "נועם": {"role": "רחפניסט", "constraints": [{"סוג": "אחר", "פירוט": "מעבר דירה", "טווח": "29/05/2026 - 29/05/2026", "דחיפות": "דרגה ג' - נמוכה", "סטטוס": "לא אושר"}]}
    }

if 'logged_in'
