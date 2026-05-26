import streamlit as st
import pandas as pd
import time
import base64
import os
from datetime import datetime, timedelta
from ortools.sat.python import cp_model

# --- הגדרות תצורה בסיסיות לעמוד ---
st.set_page_config(page_title="MiluiMate - ניהול שיבוץ מילואים", layout="centered")

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

# --- הזרקת CSS מותאם אישית לעיצוב נקי, פונטים גדולים והנגשה של הלשוניות ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        font-family: 'Assistant', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* עיצוב כותרת ראשית ענקית ונקייה */
    h1 {
        font-size: 3.2rem !important;
        color: #1e2418 !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 25px;
        letter-spacing: -1px;
    }
    
    h2 {
        font-size: 2.2rem !important;
        color: #1e2418 !important;
        font-weight: 700 !important;
        margin-top: 15px;
    }
    
    /* הנגשה והגדלה משמעותית של תוויות שדות הקלט */
    .stWidgetFormLabel, label, [data-testid="stWidgetLabel"] p {
        color: #1e2418 !important;
        font-weight: 700 !important;
        font-size: 1.2rem !important;
        margin-bottom: 8px;
    }
    
    /* שדות קלט מוגדלים וחלקים */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #1e2418 !important;
        border: 2px solid #556644 !important;
        border-radius: 8px !important;
        font-size: 1.15rem !important;
        padding: 6px !important;
    }
    
    /* עיצוב מחדש של הציון והמדדים */
    div[data-testid="stMetricValue"] {
        font-size: 2.3rem !important;
        font-weight: bold !important;
        color: #1e2418 !important;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.92);
        border: 2px solid #556644;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 6px 18px rgba(0, 0, 0, 0.1);
    }
    
    /* עיצוב כרטיסיות הטפסים */
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 16px;
        padding: 30px;
        border: 2px solid #556644 !important;
        box-shadow: 0 12px 40px rgba(0,0,0,0.1);
    }
    
    /* כפתורי הפעלה רחבים וברורים */
    .stButton>button {
        background-color: #556644;
        color: white;
        border-radius: 8px;
        border: 1px solid #3d4a31;
        padding: 12px 30px;
        font-size: 1.25rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 10px rgba(0,0,0,0.15);
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #3d4a31;
        transform: translateY(-2px);
    }
    
    /* 🚨 שדרוג והנגשה של הלשוניות (Tabs) למראה יפה וגדול 🚨 */
    button[data-baseweb="tab"] {
        font-size: 1.4rem !important; /* פונט גדול ובולט */
        font-weight: 800 !important;
        color: #4a5740 !important;
        padding: 14px 28px !important;
        background-color: rgba(255, 255, 255, 0.5) !important;
        border-radius: 10px 10px 0 0 !important;
        margin-left: 8px !important;
        border: 1px solid rgba(85, 102, 68, 0.2) !important;
        border-bottom: none !important;
        transition: all 0.2s ease;
    }
    
    /* עיצוב הלשונית שנבחרה ברגע זה */
    button[aria-selected="true"] {
        color: #ffffff !important;
        background-color: #556644 !important; /* רקע ירוק זית מודגש לטאב הפעיל */
        border-color: #556644 !important;
        box-shadow: 0px -4px 12px rgba(0,0,0,0.1);
    }
    
    /* עיצוב הטבלאות */
    .stDataFrame, [data-testid="stDataEditor"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        border-radius: 12px;
        padding: 6px;
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
        "רועי": {"role": "חובש", "constraints": [{"סוג האילוץ": "הליך רפואי", "פירוט / מלל חופשי": "ניתוח כירורגי באסותא", "טווח תאריכים": "27/05/2026 - 29/05/2026", "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"}]},
        "דניאל": {"role": "נגביסט", "constraints": []},
        "יוסי": {"role": "מפקד כיתה", "constraints": [{"סוג האילוץ": "מבחן/לימודים", "פירוט / מלל חופשי": "מבחן מועד א' בכלכלה מאקרו", "טווח תאריכים": "26/05/2026 - 26/05/2026", "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"}]},
        "אביב": {"role": "קלע", "constraints": [{"סוג האילוץ": "אירוע משפחתי", "פירוט / מלל חופשי": "חתונה של אחותי", "טווח תאריכים": "28/05/2026 - 28/05/2026", "דחיפות": "דרגה ב' - בינוני", "סטטוס": "בבדיקה"}]},
        "איתי": {"role": "נהג", "constraints": []},
        "נועם": {"role": "רחפניסט", "constraints": [{"סוג האילוץ": "אחר", "פירוט / מלל חופשי": "מעבר דירה", "טווח תאריכים": "29/05/2026 - 29/05/2026", "דחיפות": "דרגה ג' - נמוכה", "סטטוס": "לא אושר"}]}
    }

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

# --- מסך 1: התחברות ---
def login_page():
    show_logo()
    st.markdown("<h1>MiluiMate - כניסה למערכת</h1>", unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("שם משתמש:")
        password = st.text_input("סיסמה:", type="password")
        submit = st.form_submit_button("התחבר למערכת")
        
        if submit:
            if username == "mefaked" and password == "1234":
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = {"role": "commander", "name": "סרן דוד"}
                st.rerun()
            elif username == "hayal1" and password == "0000":
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = {"role": "soldier", "name": "רועי"}
                st.rerun()
            else:
                st.error("שם משתמש או סיסמה שגויים. המשתמש אינו קיים במערכת.")

# --- מסך 2: ממשק חייל (הזנת אילוצים מסווגים) ---
def soldier_page():
    show_logo()
    user_name = st.session_state['user_info']['name']
    st.markdown(f"<h2>שלום {user_name}, עדכן את אילוציך במערכת</h2>", unsafe_allow_html=True)
    
    with st.form("constraints_form"):
        st.markdown("### 📝 הגשת אילוץ חדש (מסתנכרן אוטומטית לפי דחיפות)")
        role = st.selectbox("תפקיד בכוח:", ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"])
        request_type = st.selectbox("סוג האילוץ (סיווג דחיפות):", ["הליך רפואי", "אירוע משפחתי", "סיבה אישית", "מבחן/לימודים", "אחר"])
        free_text = st.text_input("פירוט האילוץ (מלל חופשי):", placeholder="הקלד כאן פרטים נוספים...")
        
        st.markdown("**בחר את טווח התאריכים המדויק:**")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("מתאריך:", datetime.now())
        with col_d2:
            end_date = st.date_input("עד תאריך (כולל):", datetime.now() + timedelta(days=2))
            
        submit_req = st.form_submit_button("➕ שלח וסנכרן לחמ\"ל המפקד")
        
        if submit_req:
            if start_date > end_date:
                st.error("תאריך ההתחלה לא יכול להיות מאוחר מתאריך הסיום.")
            else:
                if request_type in ["הליך רפואי", "מבחן/לימודים"]:
                    priority_tier = "דרגה א' - קריטי"
                    initial_status = "אושר"
                elif request_type in ["אירוע משפחתי", "סיבה אישית"]:
                    priority_tier = "דרגה ב' - בינוני"
                    initial_status = "בבדיקה"
                else:
                    priority_tier = "דרגה ג' - נמוכה"
                    initial_status = "בבדיקה"

                formatted_range = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
                new_constraint = {
                    "סוג האילוץ": request_type,
                    "פירוט / מלל חופשי": free_text if free_text else ("נדרש פירוט" if request_type == "אחר" else "אין פירוט"),
                    "טווח תאריכים": formatted_range,
                    "דחיפות": priority_tier,
                    "סטטוס": initial_status
                }
                st.session_state['db_soldiers'][user_name]["constraints"].append(new_constraint)
                st.session_state['db_soldiers'][user_name]["role"] = role
                st.success(f"הבקשה סווגה כ-{priority_tier} וסונכרנה בהצלחה!")

    my_constraints = st.session_state['db_soldiers'][user_name]["constraints"]
    if my_constraints:
        st.markdown("### 📋 האילוצים הפעילים שלך במערכת:")
        st.table(pd.DataFrame(my_constraints))
        if st.button("🗑️ מחק את כל האילוצים שלי"):
            st.session_state['db_soldiers'][user_name]["constraints"] = []
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 התנתק מהמערכת"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- מסך 3: ממשק מפקד (לשוניות משודרגות ומעוצבות מחדש) ---
def commander_page():
    show_logo()
    st.markdown("<h1>ניהול שיבוץ - MiluiMate</h1>", unsafe_allow_html=True)
    
    # שלוש לשוניות מעוצבות כפתורים גדולים
    tab1, tab2, tab3 = st.tabs(["מסך 1: הגדרת דרישות סד\"כ", "מסך 2: פידבק סטטוס אילוצים", "מסך 3: לוח שיבוץ אופטימלי"])
    
    with tab1:
        with st.form("commander_constraints_form"):
            st.markdown("### 🛠️ קביעת אילוצים קשיחים לפלוגה")
            col1, col2 = st.columns(2)
            with col1:
                min_forces = st.number_input("סד\"כ לוחמים מינימלי חובה בבסיס (בכל יום):", min_value=1, value=6, key="cmd_min_forces")
                planning_days = st.number_input("טווח תכנון הסבב (בימים):", min_value=7, value=14)
            with col2:
                exit_format = st.selectbox("תבנית יציאות מועדפת לכוח:", ["יומי", "שבוע-שבוע", "חמשו\"ש", "יומיים"])
            
            st.markdown("---")
            st.markdown("### 🗂️ דרישת מינימום של בעלי תפקידים חיוניים")
            col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
            with col_r1:
                num_commanders = st.number_input("מפקדי כיתות:", min_value=0, value=2)
                num_drones = st.number_input("רחפניסטים:", min_value=0, value=1)
            with col_r2:
                num_medics = st.number_input("חובשים:", min_value=0, value=1)
                num_grenadiers = st.number_input("מטוליסטים:", min_value=0, value=1)
            with col_r3:
                num_sharpshooters = st.number_input("קלעים:", min_value=0, value=1)
                num_mag = st.number_input("מאגיסטים:", min_value=0, value=1)
            with col_r4:
                num_drivers = st.number_input("נהגים:", min_value=0, value=1)
                num_infantry = st.number_input("רובאי לוחם:", min_value=0, value=3)
            with col_r5:
                num_negev = st.number_input("נגביסטים:", min_value=0, value=1)
                
            st.markdown("<br>", unsafe_allow_html=True)
            save_requirements = st.form_submit_button("💾 שמור דרישות מבצעיות")
            if save_requirements:
                st.session_state['min_forces'] = min_forces
                st.session_state['exit_format'] = exit_format
                st.success("הדרישות המבצעיות נשמרו בהצלחה!")

    with tab2:
        st.markdown("### 🚦 פידבק ובקרת סטטוס אילוצים (בזמן אמת)")
        
        rows = []
        for soldier_name, data in st.session_state['db_soldiers'].items():
            if data["constraints"]:
                for c in data["constraints"]:
                    rows.append({
                        "שם החייל": soldier_name,
                        "תפקיד / פק\"ל": data["role"],
                        "סיווג האילוץ": c["סוג האילוץ"],
                        "טווח תאריכים": c["טווח תאריכים"] if "טווח תאריכים" in c else c.get("טווח", "-"),
                        "סיווג דחיפות": c["דחיפות"],
                        "סטטוס בקשה": c["סטטוס"]
                    })
            else:
                rows.append({
                    "שם החייל": soldier_name,
                    "תפקיד / פק\"ל": data["role"],
                    "סיווג האילוץ": "אין אילוצים",
                    "טווח תאריכים": "-",
                    "סיווג דחיפות": "-",
                    "סטטוס בקשה": "כשיר לפעילות"
                })
        
        df_feedback = pd.DataFrame(rows)

        def color_rows(row):
            status = row["סטטוס בקשה"]
            if status == "אושר":
                return ['background-color: rgba(144, 238, 144, 0.4); color: black'] * len(row)
            elif status == "לא אושר":
                return ['background-color: rgba(255, 182, 193, 0.5); color: black'] * len(row)
            elif status == "בבדיקה":
                return ['background-color: rgba(255, 239, 204, 0.6); color: black'] * len(row)
            return [''] * len(row)

        styled_feedback = df_feedback.style.apply(color_rows, axis=1)
        st.dataframe(styled_feedback, use_container_width=True)
        
        st.markdown("#### ✍️ שינוי ידני מהיר של סטטוס אילוץ:")
        col_sel1, col_sel2, col_sel3 = st.columns(3)
        with col_sel1:
            chosen_soldier = st.selectbox("בחר חייל:", list(st.session_state['db_soldiers'].keys()))
        with col_sel2:
            new_status_choice = st.selectbox("קבע סטטוס חדש:", ["אושר", "לא אושר", "בבדיקה"])
        with col_sel3:
            st
