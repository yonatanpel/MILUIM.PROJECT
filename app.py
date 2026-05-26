import streamlit as st
import pandas as pd
import time
import base64
import os
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
    
    /* אלמנט ה-CSS להעלמת הרקע הלבן מהלוגו */
    [data-testid="stImage"] {
        mix-blend-mode: multiply;
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
        # מנגנון חכם שמוודא מציאת הלוגו גם אם יש הבדל בסיומת או באותיות גדולות/קטנות
        possible_names = ["logo.jpeg", "logo.jpg", "logo.png", "LOGO.jpeg", "LOGO.JPG", "LOGO.PNG", "Logo.jpeg"]
        logo_found = False
        
        for name in possible_names:
            if os.path.exists(name):
                st.image(name, use_container_width=True)
                logo_found = True
                break
                
        if not logo_found:
            st.warning("לוגו המערכת לא נמצא בתיקיית הריצה הראשי.")

def authenticate(username, password):
    users = {
        "mefaked": {"pass": "1234", "role": "commander", "name": "סרן דוד"},
        "hayal1": {"pass": "0000", "role": "soldier", "name": "רועי"},
    }
    if username in users and users[username]["pass"] == password:
        return users[username]
    return None

# --- ניהול State ---
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

# --- מסך 1: התחברות ---
def login_page():
    show_logo()
    st.markdown("<h2 style='text-align: center;'>MiluiMate - כניסה למערכת</h2>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("שם משתמש:")
        password = st.text_input("סיסמה:", type="password")
        submit = st.form_submit_button("התחבר")
        
        if submit:
            user = authenticate(username, password)
            if user:
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = user
                st.rerun()
            else:
                st.error("שם משתמש או סיסמה שגויים. המשתמש אינו קיים במערכת.")

# --- מסך 2: ממשק חייל ---
def soldier_page():
    show_logo()
    user_name = st.session_state
