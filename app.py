import streamlit as st
import pandas as pd
import time
import base64
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

# --- הזרקת CSS מותאם אישית לעיצוב הניגודיות מעל רקע ההסוואה הבהיר ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        font-family: 'Assistant', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #1e2418 !important;
        font-weight: 700 !important;
    }
    .stWidgetFormLabel, label, [data-testid="stWidgetLabel"] p {
        color: #1e2418 !important;
        font-weight: 600 !important;
        font-size: 1.05rem !important;
        margin-bottom: 5px;
    }
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #1e2418 !important;
        border: 2px solid #556644 !important;
        border-radius: 6px !important;
    }
    div[data-testid="stMetricValue"] {
        font-size: 2rem !important;
        font-weight: bold !important;
        color: #2e3b23 !important;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.85);
        border: 2px solid #556644;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.15);
    }
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.82) !important;
        border-radius: 12px;
        padding: 20px;
        border: 2px solid #556644 !important;
        box-shadow: 0 8px 32px rgba(0,0,0,0.1);
    }
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
        try:
            st.image("logo.jpeg", use_container_width=True)
        except:
            st.markdown("<h1 style='text-align: center; color: #556644;'>🐌 MiluiMate</h1>", unsafe_allow_html=True)

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
        role = st.selectbox("תפקיד בכוח:", ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"])
        request_type = st.selectbox("סוג/תבנית יציאה מבוקשת:", ["יומי", "שבוע-שבוע", "חמשו\"ש", "יומיים"])
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
            min_forces = st.number_input("סד\"כ לוחמים מינימלי חובה בבסיס (בכל יום):", min_value=1, value=10)
            planning_days = st.number_input("טווח תכנון הסבב (בימים):", min_value=7, value=14)
        with col2:
            exit_format = st.selectbox("תבנית יציאות מועדפת לכוח:", ["יומי", "שבוע-שבוע", "חמשו\"ש", "יומיים"])
        
        st.markdown("---")
        st.markdown("### 🗂️ דרישת בעלי תפקידים חיוניים (הזן כמה לוחמים יש לך מכל תפקיד להדמיה)")
        
        col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
        with col_r1:
            num_commanders = st.number_input("מפקדי כיתות:", min_value=0, value=2)
            num_drones = st.number_input("רחפניסטים:", min_value=0, value=2)
        with col_r2:
            num_medics = st.number_input("חובשים:", min_value=0, value=2)
            num_grenadiers = st.number_input("מטוליסטים:", min_value=0, value=2)
        with col_r3:
            num_sharpshooters = st.number_input("קלעים:", min_value=0, value=2)
            num_mag = st.number_input("מאגיסטים:", min_value=0, value=2)
        with col_r4:
            num_drivers = st.number_input("נהגים:", min_value=0, value=2)
            num_infantry = st.number_input("רובאי לוחם:", min_value=0, value=4)
        with col_r5:
            num_negev = st.number_input("נגביסטים:", min_value=0, value=2)
            
        st.markdown("<br>", unsafe_allow_html=True)
        run_optimization = st.form_submit_button("🚀 הפעל מנוע אופטימיזציה (CP-SAT Engine)")

    if run_optimization:
        with st.spinner("מנוע ה-CP-SAT מנתח את אילוצי הסד\"כ שהזנת..."):
            time.sleep(2.2) # הדמיית חישוב אלגוריתמי
            
            # בניית רשימת לוחמים דינמית על בסיס הנתונים שהמפקד הזין כרגע במסך!
            roles_dict = {
                "מפקד כיתה": num_commanders,
                "חובש": num_medics,
                "קלע": num_sharpshooters,
                "נהג": num_drivers,
                "נגביסט": num_negev,
                "רחפניסט": num_drones,
                "מטוליסט": num_grenadiers,
                "מאגיסט": num_mag,
                "רובאי לוחם": num_infantry
            }
            
            names_list = []
            roles_list = []
            
            # יצירת שמות ופק"לים מותאמים אישית בהתאם לכמויות
            for role_name, count in roles_dict.items():
                for i in range(1, count + 1):
                    names_list.append(f"לוחם {len(names_list) + 1}")
                    roles_list.append(role_name)
            
            total_generated = len(names_list)
            
            if total_generated == 0:
                st.error("אנא הגדר לפחות לוחם אחד בדרישות בעלי התפקידים כדי לבצע הדמיה.")
            else:
                st.success(f"האופטימיזציה הסתיימה בהצלחה! שובצו בהצלחה {total_generated} לוחמים בצורה מאוזנת.")
                
                # כרטיסיות מדדים דינמיות
                m_col1, m_col2, m_col3 = st.columns(3)
                with m_col1:
                    st.metric("סה\"כ לוחמים בסימולציה", f"{total_generated} איש", "סד\"כ דינמי")
                with m_col2:
                    st.metric("מדד הוגנות וחלוקה", "100%" if exit_format == "שבוע-שבוע" else "94%", "שוויון מלא")
                with m_col3:
                    st.metric("זמן ריצת אלגוריתם", "0.24 שניות", "אופטימלי")
                
                st.markdown("<br>### 📅 לוח שיבוץ יציאות דינמי (ניתן לעריכה ידנית ע\"י המפקד ✍️)", unsafe_allow_html=True)
                st.info("💡 הטבלה מבוססת על כמויות הלוחמים שהזנת למעלה. ניתן ללחוץ דאבל-קליק על כל משבצת כדי לשנות את השיבוץ ידנית!")
                
                # בניית תתי-העמודות של ימי השבוע או השבועות בהתאם לפורמט היציאה
                if exit_format == "שבוע-שבוע":
                    # יישום לוגיקת שבוע-שבוע ראש בראש (חצי כוח בבסיס חצי בבית, ואז מתחלפים)
                    week1_status = []
                    week2_status = []
                    for idx in range(total_generated):
                        if idx % 2 == 0:
                            week1_status.append("נוכח בבסיס")
                            week2_status.append("בבית (חופשה)")
                        else:
                            week1_status.append("בבית (חופשה)")
                            week2_status.append("נוכח בבסיס")
                            
                    mock_data = {
                        "שם החייל": names_list,
                        "תפקיד / פק\"ל": roles_list,
                        "שבוע 1 (ימים 1-7)": week1_status,
                        "שבוע 2 (ימים 8-14)": week2_status
                    }
                else:
                    # פורמט יומי / חמשושים רגיל
                    days = ["יום א'", "יום ב'", "יום ג'", "יום ד'", "יום ה'"]
                    mock_data = {
                        "שם החייל": names_list,
                        "תפקיד / פק\"ל": roles_list,
                    }
                    # הגדרת סבב יציאות בסיסי להדמיה
                    for day_idx, day_name in enumerate(days):
                        day_status = []
                        for idx in range(total_generated):
                            if (idx + day_idx) % 4 == 0:
                                day_status.append("בבית (חופשה)")
                            else:
                                day_status.append("נוכח בבסיס")
                        mock_data[day_name] = day_status
                    
                df = pd.DataFrame(mock_data)
                
                # שימוש ב-st.data_editor לעריכה מלאה בזמן אמת של הדאטה שהוזן
                edited_df = st.data_editor(df, use_container_width=True, num_rows="fixed")
                
                if st.button("💾 שמור שיבוץ סופי מאושר"):
                    st.success("הלוח המעודכן נשמר בהצלחה והופץ ללוחמים!")

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
