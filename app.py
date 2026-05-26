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
        try:
            # חזרה לפקודה מובנית ונקייה שמונעת שגיאות סינטקס
            st.image("צילום מסך 2026-05-26 151245.png", use_container_width=True)
        except:
            st.warning("לוגו MiluiMate לא נמצא בתיקייה.")

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
    user_name = st.session_state['user_info']['name']
    st.markdown(f"<h2 style='text-align: center;'>שלום {user_name}, שלח את העדפותיך במערכת MiluiMate</h2>", unsafe_allow_html=True)
    
    with st.form("constraints_form"):
        # תפקידים מעודכנים לפי הדרישה
        role = st.selectbox("תפקיד בכוח:", ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט"])
        # תבניות יציאה מעודכנות לפי הדרישה
        request_type = st.selectbox("סוג/תבנית יציאה מבוקשת:", ["יומי", "שבוע-שבוע", "חמשש", "יומיים"])
        dates = st.date_input("תאריכים מבוקשים ליציאה:")
        submit_req = st.form_submit_button("שלח בקשה למפקד")
        
        if submit_req:
            st.success("בקשתך נקלטה במערכת בהצלחה ותלקח בחשבון בריצה הבאה!")
            
    if st.button("התנתק"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- מסך 3: ממשק מפקד ---
def commander_page():
    show_logo()
    st.markdown("<h2 style='text-align: center;'>שלום מפקד יקר, ברוך הבא ל-MiluiMate</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #3d4a31; font-weight: bold;'>כאן תוכל להגדיר את דרישות הסד\"כ המבצעיות ולהפיק לוח יציאות אופטימלי</p>", unsafe_allow_html=True)
    
    with st.form("commander_constraints_form"):
        st.markdown("### 🛠️ הגדרת אילוצי סד\"כ כלליים")
        col1, col2 = st.columns(2)
        with col1:
            min_forces = st.number_input("סד\"כ לוחמים מינימלי חובה בבסיס (בכל יום):", min_value=1, value=15)
            planning_days = st.number_input("טווח תכנון הסבב (בימים):", min_value=7, value=14)
        with col2:
            # תבניות יציאה מעודכנות לבחירת המפקד
            exit_format = st.selectbox("תבנית יציאות מועדפת לכוח:", ["יומי", "שבוע-שבוע", "חמשש", "יומיים"])
        
        st.markdown("---")
        st.markdown("### 🗂️ דרישת בעלי תפקידים חיוניים (נוכחות חובה בכל יום)")
        
        # התאמת תיבות הקלט לתפקידים החדשים
        col_role1, col_role2, col_role3, col_role4, col_role5 = st.columns(5)
        with col_role1:
            min_commanders = st.number_input("מפקדי כיתות:", min_value=0, value=3)
        with col_role2:
            min_medics = st.number_input("חובשים:", min_value=0, value=2)
        with col_role3:
            min_snipers = st.number_input("קלעים:", min_value=0, value=2)
        with col_role4:
            min_drivers = st.number_input("נהגים:", min_value=0, value=1)
        with col_role5:
            min_negev = st.number_input("נגביסטים:", min_value=0, value=1)
            
        st.markdown("<br>", unsafe_allow_html=True)
        run_optimization = st.form_submit_button("🚀 הפעל מנוע אופטימיזציה (CP-SAT Engine)")

    if run_optimization:
        with st.spinner("מנוע ה-CP-SAT מנתח מיליוני שילובים אפשריים..."):
            model = cp_model.CpModel()
            time.sleep(2.5) # הדמיית ריצה
            
            st.success("האופטימיזציה הסתיימה בהצלחה! נמצא פתרון אופטימלי המאזן בין המשימה לחיילים.")
            
            # הצגת המדדים
            m_col1, m_col2, m_col3 = st.columns(3)
            with m_col1:
                st.metric("סטיית תקן (מדד שוויון)", "0.8 ימים", "שיפור בהוגנות")
            with m_col2:
                st.metric("אחוז בקשות פרט שנענו", "94%", "מקסימום אפשרי")
            with m_col3:
                st.metric("זמן ריצת אלגוריתם", "0.42 שניות", "יציב")
            
            st.markdown("<br>### 📅 לוח שיבוץ יציאות אופטימלי (טיוטה ראשונית למפקד)", unsafe_allow_html=True)
            
            # טבלה מעודכנת עם התפקידים החדשים
            mock_data = {
                "שם החייל": ["רועי", "דניאל", "יוסי", "אביב", "איתי", "נועם"],
                "תפקיד בכוח": ["חובש", "נגביסט", "מפקד כיתה", "קלע", "נהג", "קלע"],
                "יום א'": ["נוכח בבסיס", "בבית (חופשה)", "נוכח בבסיס", "נוכח בבסיס", "נוכח בבסיס", "נוכח בבסיס"],
                "יום ב'": ["נוכח בבסיס", "נוכח בבסיס", "נוכח בבסיס", "בבית (חופשה)", "נוכח בבסיס", "נוכח בבסיס"],
                "יום ג'": ["בבית (חופשה)", "נוכח בבסיס", "בבית (חופשה)", "נוכח בבסיס", "נוכח בבסיס", "נוכח בבסיס"],
                "יום ד'": ["נוכח בבסיס", "נוכח בבסיס", "נוכח בבסיס", "נוכח בבסיס", "בבית (חופשה)", "נוכח בבסיס"],
                "יום ה'": ["נוכח בבסיס", "נוכח בבסיס", "נוכח בבסיס", "נוכח בבסיס", "נוכח בבסיס", "בבית (חופשה)"],
            }
            df = pd.DataFrame(mock_data)
            st.dataframe(df.style.set_properties(**{'text-align': 'right'}), use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 התנתק מהמערכת"):
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
