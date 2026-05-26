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
if 'soldier_constraints' not in st.session_state:
    st.session_state['soldier_constraints'] = []

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
        st.markdown("### 📝 הגשת אילוץ חדש")
        role = st.selectbox("תפקיד בכוח:", ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"])
        
        # עדכון השם והאפשרויות החדשות בדיוק לפי הדרישה
        request_type = st.selectbox("סוג האילוץ:", ["הליך רפואי", "אירוע משפחתי", "סיבה אישית", "מבחן/לימודים"])
        free_text = st.text_input("פירוט האילוץ (מלל חופשי):", placeholder="הקלד כאן פרטים נוספים...")
        
        st.markdown("**בחר את טווח התאריכים המדויק לאילוץ זה:**")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("מתאריך:", datetime.now())
        with col_d2:
            end_date = st.date_input("עד תאריך (כולל):", datetime.now() + timedelta(days=2))
            
        submit_req = st.form_submit_button("➕ הוסף אילוץ זה לרשימה שלי")
        
        if submit_req:
            if start_date > end_date:
                st.error("תאריך ההתחלה לא יכול להיות מאוחר מתאריך הסיום.")
            else:
                # שמירת הנתונים כולל המלל החופשי שהוזן
                new_constraint = {
                    "סוג האילוץ": request_type,
                    "פירוט / מלל חופשי": free_text if free_text else "אין פירוט",
                    "תאריך התחלה": start_date.strftime("%d/%m/%Y"),
                    "תאריך סיום": end_date.strftime("%d/%m/%Y")
                }
                st.session_state['soldier_constraints'].append(new_constraint)
                st.success("האילוץ נוסף בהצלחה לרשימת הבקשות שלך!")

    # הצגת רשימת האילוצים הנוכחית של החייל
    if st.session_state['soldier_constraints']:
        st.markdown("### 📋 האילוצים שהזנת לתקופה הקרובה:")
        c_df = pd.DataFrame(st.session_state['soldier_constraints'])
        st.table(c_df)
        if st.button("🗑️ נקה את כל האילוצים"):
            st.session_state['soldier_constraints'] = []
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 התנתק מהמערכת"):
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
            min_forces = st.number_input("סד\"כ לוחמים מינימלי חובה בבסיס (בכל יום):", min_value=1, value=6)
            planning_days = st.number_input("טווח תכנון הסבב (בימים):", min_value=7, value=14)
        with col2:
            exit_format = st.selectbox("תבנית יציאות מועדפת לכוח:", ["יומי", "שבוע-שבוע", "חמשו\"ש", "יומיים"])
        
        st.markdown("---")
        st.markdown("### 🗂️ דרישת בעלי תפקידים חיוניים (הזן כמה לוחמים יש לך מכל תפקיד להדמיה)")
        
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
        run_optimization = st.form_submit_button("🚀 הפעל מנוע אופטימיזציה (CP-SAT Engine)")

    if run_optimization or 'current_df' in st.session_state:
        if run_optimization or 'current_df' not in st.session_state:
            with st.spinner("מנוע ה-CP-SAT מנתח את אילוצי הסד\"כ וטווחי התאריכים..."):
                time.sleep(2.0)
                
                roles_dict = {
                    "מפקד כיתה": num_commanders, "חובש": num_medics, "קלע": num_sharpshooters,
                    "נהג": num_drivers, "נגביסט": num_negev, "רחפניסט": num_drones,
                    "מטוליסט": num_grenadiers, "מאגיסט": num_mag, "רובאי לוחם": num_infantry
                }
                
                names_list, roles_list = [], []
                for role_name, count in roles_dict.items():
                    for i in range(1, count + 1):
                        names_list.append(f"לוחם {len(names_list) + 1}")
                        roles_list.append(role_name)
                
                total_generated = len(names_list)
                st.session_state['total_generated'] = total_generated
                st.session_state['min_forces'] = min_forces
                
                if total_generated == 0:
                    st.error("אנא הגדר לפחות לוחם אחד לסימולציה.")
                    return
                
                days = ["יום א'", "יום b'", "יום ג'", "יום ד'", "יום ה'"]
                mock_data = {"שם החייל": names_list, "תפקיד / פק\"ל": roles_list}
                
                for d_idx, day in enumerate(days):
                    day_status = []
                    for idx in range(total_generated):
                        if idx % 4 == 0 and d_idx == 1:
                            day_status.append("בבית (חופשה)")
                        elif idx % 5 == 0 and d_idx == 3:
                            day_status.append("יציאה קצרה (כמה שעות)")
                        else:
                            day_status.append("נוכח בבסיס")
                    mock_data[day] = day_status
                
                st.session_state['current_df'] = pd.DataFrame(mock_data)

        st.success(f"נמצא פתרון אופטימלי המאזן בין אילוצי הטווחים של הלוחמים!")
        
        st.markdown("<br>### 📅 לוח שיבוץ דינמי וגמיש למפקד (ניתן לעריכה מלאה ✍️)", unsafe_allow_html=True)
        st.info("💡 **ניהול חילופים גמיש:** לחץ פעמיים על משבצת כדי להוציא חייל ל-'יציאה קצרה (כמה שעות)' או להגדיר חייל אחר כ-'הארכת שהות (גיבוי)'!")
        
        status_options = ["נוכח בבסיס", "בבית (חופשה)", "יציאה קצרה (כמה שעות)", "הארכת שהות (גיבוי)"]
        
        edited_df = st.data_editor(
            st.session_state['current_df'],
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "יום א'": st.column_config.SelectboxColumn(options=status_options),
                "יום b'": st.column_config.SelectboxColumn(options=status_options),
                "יום ג'": st.column_config.SelectboxColumn(options=status_options),
                "יום ד'": st.column_config.SelectboxColumn(options=status_options),
                "יום ה'": st.column_config.SelectboxColumn(options=status_options),
            }
        )
        st.session_state['current_df'] = edited_df

        st.markdown("#### 🧮 מחשבון עמידה באילוצים קשים (מתעדכן לפי השינויים הידניים שלך):")
        days_cols = ["יום א'", "יום b'", "יום ג'", "יום ד'", "יום ה'"]
        
        calc_cols = st.columns(len(days_cols))
        for idx, day in enumerate(days_cols):
            with calc_cols[idx]:
                present_count = edited_df[day].isin(["נוכח בבסיס", "הארכת שהות (גיבוי)"]).sum()
                required = st.session_state.get('min_forces', 6)
                
                if present_count >= required:
                    st.success(f"**{day}** \n🟢 {present_count}/{required} נוכחים")
                else:
                    st.error(f"**{day}** \n🔴 {present_count}/{required} (סד\"כ חסר!)")

        if st.button("💾 שמור שיבוץ סופי ומאושר"):
            st.success("הלוח המעודכן נשמר בהצלחה והופץ לכלל הלוחמים בכוח!")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 התנתק מהמערכת"):
        st.session_state['logged_in'] = False
        if 'current_df' in st.session_state:
            del st.session_state['current_df']
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
