import streamlit as st
import pandas as pd
import time
from ortools.sat.python import cp_model

# --- הגדרות תצורה בסיסיות לעמוד ---
st.set_page_config(page_title="מערכת שיבוץ מילואים - MiluiMate", layout="centered")

# --- הזרקת CSS מותאם אישית לעיצוב צבאי, יישור לימין (RTL) ותיקון הניגודיות ---
st.markdown("""
    <style>
    /* הפיכת כיוון הטקסט לימין-לשמאל */
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        font-family: 'Assistant', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    /* עיצוב רקע האפליקציה לצבע צבאי עדין */
    .stApp {
        background-color: #2b3323; /* ירוק זית כהה */
        color: #e6e5df; /* אפור-בז' בהיר לטקסט כללי */
    }
    
    /* תיקון קריטי: צביעת כל תוויות התיאור של הקלטים בלבן כדי שיראו אותן בבירור */
    .stWidgetFormLabel, label, [data-testid="stWidgetLabel"] p {
        color: #ffffff !important;
        font-weight: bold !important;
        font-size: 1.05rem !important;
    }
    
    /* עיצוב פנים תיבות הקלט (Inputs) */
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #434f36 !important;
        color: white !important;
        border: 1px solid #5a6b47 !important;
    }
    
    /* כפתורים */
    .stButton>button {
        background-color: #6d8055;
        color: white;
        border-radius: 8px;
        border: none;
        width: 100%;
        font-weight: bold;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #5a6b47;
        color: #ffffff;
    }
    
    /* עיצוב התראות ואדום לשגיאות */
    .stAlert {
        direction: rtl;
    }
    </style>
""", unsafe_allow_html=True)

# --- פונקציות עזר ---
def show_logo():
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        # שימוש בשם הקובץ המדויק שהעלית לגיטאהב
        try:
            st.image("צילום מסך 2026-05-26 151245.png", use_container_width=True)
        except:
            st.warning("לוגו MiluiMate לא נמצא בתיקייה. נא לוודא ששם הקובץ בגיטאהב תואם בדיוק.")

def authenticate(username, password):
    # מסד נתונים וירטואלי (Mock) לצורך הדגמה - יוחלף ב-SQL בהמשך
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
if 'soldier_requests' not in st.session_state:
    st.session_state['soldier_requests'] = []

# --- מסך 1: התחברות ---
def login_page():
    show_logo()
    st.markdown("<h2 style='text-align: center; color: white;'>MiluiMate - כניסה למערכת</h2>", unsafe_allow_html=True)
    
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
    user_name = st.session_state['user_info']['name']
    st.markdown(f"<h2 style='text-align: center; color: white;'>ברוך הבא, {user_name}</h2>", unsafe_allow_html=True)
    st.markdown("### הזנת אילוצים ובקשות יציאה")
    
    with st.form("constraints_form"):
        role = st.selectbox("תפקיד בכוח:", ["לוחם פלוגתי", "מפקד כיתה", "חובש", "קלע", "צלף", "נהג מבצעי"])
        request_type = st.selectbox("סוג בקשה:", ["העדפה ליציאה", "אילוץ קשיח (אירוע משפחתי וכו')"])
        dates = st.date_input("תאריכים מבוקשים ליציאה:")
        submit_req = st.form_submit_button("שלח בקשה למפקד")
        
        if submit_req:
            st.session_state['soldier_requests'].append({
                "name": user_name, "role": role, "type": request_type, "date": dates
            })
            st.success("בקשתך נקלטה במערכת MiluiMate בהצלחה!")
            
    if st.button("התנתק"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- מסך 3: ממשק מפקד (אופטימיזציה ב-OR-Tools) ---
def commander_page():
    show_logo()
    st.markdown("<h2 style='text-align: center; color: white;'>מסוף פיקוד - הרצת אופטימיזציה (MiluiMate Engine)</h2>", unsafe_allow_html=True)
    
    st.markdown("### הגדרת אילוצים מבצעיים (קשיחים)")
    with st.form("commander_constraints_form"):
        col1, col2 = st.columns(2)
        with col1:
            min_forces = st.number_input("סד\"כ מינימלי נדרש בבסיס (ליום):", min_value=1, value=15)
            min_medics = st.number_input("מספר חובשים מינימלי בבסיס:", min_value=1, value=2)
        with col2:
            exit_format = st.selectbox("דרישת/תבנית יציאות כללית:", ["ללא מוגדר (חישוב חופשי)", "חמשוש", "אפטר שבועי", "שבוע-שבוע"])
            planning_days = st.number_input("טווח תכנון (ימים):", min_value=7, value=14)
        
        st.markdown("<br>", unsafe_allow_html=True)
        run_optimization = st.form_submit_button("🚀 הפעל מנוע אופטימיזציה (CP-SAT)")

    if run_optimization:
        with st.spinner("בונה מודל ומשקלל אילוצים..."):
            model = cp_model.CpModel()
            time.sleep(2) # הדמיית ריצה קומבינטורית
            
            st.success("האופטימיזציה הסתיימה בהצלחה. נמצא פתרון אופטימלי גלובלי!")
            
            # מדדי הצלחה מהאפיון
            m_col1, m_col2, m_col3 = st.columns(3)
            m_col1.metric("סטיית תקן (מדד שוויון)", "0.8 ימים", "-0.2")
            m_col2.metric("אחוז בקשות שאושרו", "94%", "+4%")
            m_col3.metric("זמן ריצה", "0.42 שניות")
            
            st.markdown("### 📅 שיבוץ אופטימלי שנוצר (טיוטה ראשונית)")
            mock_data = {
                "שם החייל": ["רועי", "דניאל", "יוסי", "אביב"],
                "תפקיד": ["חובש", "לוחם", "מפקד כיתה", "קלע"],
                "סטטוס יום א'": ["בסיס", "בבית", "בסיס", "בסיס"],
                "סטטוס יום ב'": ["בסיס", "בסיס", "בסיס", "בבית"],
                "סטטוס יום ג'": ["בבית", "בסיס", "בבית", "בסיס"],
            }
            df = pd.DataFrame(mock_data)
            st.dataframe(df, use_container_width=True)

    if st.button("התנתק"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- ניתוב דפים ---
def main():
    if not st.session_state['logged_in']:
        login_page()
    else:
        role = st.session_state['user_info']['role']
        if role == "commander":
            commander_page()
        elif role == "soldier":
            soldier_page()

if __name__ == "__main__":
    main()
