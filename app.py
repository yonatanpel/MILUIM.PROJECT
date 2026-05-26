import streamlit as st
import pandas as pd
import time
import base64
from ortools.sat.python import cp_model

# --- הגדרות תצורה בסיסיות לעמוד ---
st.set_page_config(page_title="MiluiMate - ניהול שיבוץ מילואים", layout="centered")

# --- פונקציה להמרת תמונת הרקע המקומית ל-Base64 ---
def get_base64_of_bin_file(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# ניסיון טעינת רקע ההסוואה שהעלית
try:
    bin_str = get_base64_of_bin_file('IMG_5952.JPG')
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
except:
    # גיבוי במידה והקובץ לא נמצא זמנית בשרת
    st.markdown("""
        <style>
        .stApp { background-color: #e6e5df; }
        </style>
    """, unsafe_allow_html=True)

# --- הזרקת CSS מותאם אישית לעיצוב הניגודיות מעל רקע ההסוואה הבהיר ---
st.markdown("""
    <style>
    /* הפיכת כיוון הטקסט לימין-לשמאל */
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        font-family: 'Assistant', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* התאמת צבעי הכותרות שייראו בבירור על רקע בהיר */
    h1, h2, h3, h4, h5, h6 {
        color: #1e2418 !important; /* ירוק זית כהה מאוד / שחור */
        font-weight: 700 !important;
    }
    
    /* תוויות התיאור של שדות הקלט */
    .stWidgetFormLabel, label, [data-testid="stWidgetLabel"] p {
        color: #1e2418 !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        margin-bottom: 5px;
    }
    
    /* עיצוב שדות הקלט - קונטרסט כהה בתוך התיבות */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #1e2418 !important;
        border: 2px solid #556644 !important;
        border-radius: 6px !important;
    }
    
    /* עיצוב כרטיסיות המדדים (Metrics Blocks) */
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: bold !important;
        color: #2e3b23 !important; /* צבע כהה ובולט */
    }
    
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.85); /* רקע לבן חצי שקוף */
        border: 2px solid #556644;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
    }
    
    /* עיצוב טפסים (Forms) */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.82) !important; /* הגברת הניגודיות והחלקה של הבלוק */
        border-radius: 12px;
        padding: 20px;
        border: 2px solid #556644 !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
    
    /* עיצוב כפתורים */
    .stButton>button {
        background-color: #556644;
        color: white;
        border-radius: 8px;
        border: 1px solid #3d4a31;
        padding: 10px 20px;
        font-size: 1.1rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0px 3px 6px rgba(0,0,0,0.2);
    }
    
    .stButton>button:hover {
        background-color: #3d4a31;
        color: #ffffff;
        transform: translateY(-2px);
    }
    
    /* התראות */
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
        # שימוש בטכניקת mix-blend-mode להטמעה נקייה של הלוגו מעל רקע ההסוואה
        st.markdown(
            """
            <div style="display: flex; justify-content: center; mix-blend-mode: multiply;">
                <img src="
