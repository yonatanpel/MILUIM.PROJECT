import streamlit as st
import pandas as pd
import time
import base64
import os
from datetime import datetime, timedelta
from ortools.sat.python import cp_model

# --- הגדרות תצורה בסיסיות לעמוד ---
st.set_page_config(page_title="MiluiMate - מערכת שיבוץ חכמה", layout="centered")

# --- פונקציה להמרת תמונת הרקע המקומית ל-Base64 ---
def get_base64_of_bin_file(bin_file):
    try:
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
    except:
        return None

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

# --- הזרקת CSS מותאם אישית - יישור, פונטים וטבלאות ---
st.markdown("""
    <style>
    html, body, [class*="css"], .stApp  {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Assistant', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    .stWidgetFormLabel, label, [data-testid="stWidgetLabel"] p, .stMarkdown p {
        text-align: right !important;
        direction: rtl !important;
        color: #1e2418 !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        margin-bottom: 8px;
    }
    
    h1 {
        font-size: 3.2rem !important;
        color: #1e2418 !important;
        font-weight: 800 !important;
        text-align: center !important;
        margin-bottom: 30px;
    }
    
    h2 {
        font-size: 2.2rem !important;
        color: #1e2418 !important;
        font-weight: 700 !important;
        margin-top: 15px;
        text-align: right !important;
    }
    
    div[data-testid="stForm"] h3 {
        text-align: center !important;
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input, .stDateInput>div>div>input {
        background-color: #ffffff !important;
        color: #1e2418 !important;
        border: 2px solid #556644 !important;
        border-radius: 8px !important;
        font-size: 1.2rem !important;
        padding: 8px !important;
        text-align: right !important;
        direction: rtl !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2.4rem !important;
        font-weight: bold !important;
        color: #1e2418 !important;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.94);
        border: 2px solid #556644;
        padding: 20px;
        border-radius: 12px;
        box-shadow: 0px 6px 18px rgba(0, 0, 0, 0.08);
    }
    
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.92) !important;
        border-radius: 16px;
        padding: 35px;
        border: 2px solid #556644 !important;
        box-shadow: 0 12px 45px rgba(0,0,0,0.1);
    }
    
    .stButton>button {
        background-color: #556644;
        color: white;
        border-radius: 8px;
        border: 1px solid #3d4a31;
        padding: 14px 35px;
        font-size: 1.3rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 12px rgba(0,0,0,0.15);
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #3d4a31;
        transform: translateY(-2px);
    }
    
    button[data-baseweb="tab"] {
        font-size: 1.45rem !important;
        font-weight: 800 !important;
        color: #4a5740 !important;
        padding: 14px 35px !important;
        background-color: rgba(255, 255, 255, 0.6) !important;
        border-radius: 10px 10px 0 0 !important;
        margin-left: 10px !important;
        border: 2px solid rgba(85, 102, 68, 0.2) !important;
        border-bottom: none !important;
        transition: all 0.2s ease;
    }
    
    button[aria-selected="true"] {
        color: #ffffff !important;
        background-color: #556644 !important;
        border-color: #556644 !important;
        box-shadow: 0px -4px 15px rgba(0,0,0,0.12);
    }
    
    .stDataFrame, [data-testid="stDataEditor"] {
        background-color: rgba(255, 255, 255, 0.96) !important;
        border-radius: 12px;
        padding: 8px;
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

# --- פונקציות עזר ופונקציית לוגיקת תאריכים ---
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

# ממיר מחרוזת של טווח תאריכים ("DD/MM/YYYY - DD/MM/YYYY") לאובייקטי datetime
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

# פונקציית צביעה ייעודית לטבלת השיבוצים (מסך 3)
def color_schedule(val):
    if isinstance(val, str):
        if "בבית (חופשה)" in val:
            return 'background-color: #c3e6cb; color: #155724; font-weight: bold;' # ירוק
        elif "נוכח בבסיס" in val:
            return 'background-color: #f5c6cb; color: #721c24;' # אדום/ורוד
        elif "יציאה קצרה" in val:
            return 'background-color: #ffeeba; color: #856404;' # צהוב
        elif "הארכת שהות" in val:
            return 'background-color: #bee5eb; color: #0c5460;' # תכלת
    return ''

# --- אתחול בסיס נתונים ---
if 'db_soldiers' not in st.session_state:
    db = {}
    roles_pool = ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"]
    
    soldier_idx = 1
    for dept in [1, 2, 3]:
        for i in range(1, 21):
            s_name = f"לוחם {soldier_idx}"
            s_role = roles_pool[(soldier_idx - 1) % len(roles_pool)]
            
            constraints = []
            if soldier_idx == 3:
                constraints.append({"סוג האילוץ": "הליך רפואי", "פירוט / מלל חופשי": "ביקור רופא מומחה", "טווח תאריכים": (datetime.now() + timedelta(days=2)).strftime("%d/%m/%Y") + " - " + (datetime.now() + timedelta(days=4)).strftime("%d/%m/%Y"), "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"})
            elif soldier_idx == 24:
                constraints.append({"סוג האילוץ": "מבחן/לימודים", "פירוט / מלל חופשי": "מבחן סמסטר", "טווח תאריכים": (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y") + " - " + (datetime.now() + timedelta(days=1)).strftime("%d/%m/%Y"), "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"})
            else:
                constraints.append({"סוג האילוץ": "אין לי העדפה", "פירוט / מלל חופשי": "זמין לסבב מחלקתי הוגן", "טווח תאריכים": "-", "דחיפות": "סבב רגיל", "סטטוס": "אושר"})
                
            db[s_name] = {
                "role": s_role,
                "department": dept,
                "constraints": constraints
            }
            soldier_idx += 1
            
    st.session_state['db_soldiers'] = db

if 'users_db' not in st.session_state:
    st.session_state['users_db'] = {
        "mefaked": {"pass": "1234", "role": "commander", "name": "מפקד מחלקה"},
        "hayal1": {"pass": "0000", "role": "soldier", "name": "לוחם 3"},
    }

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None
if 'dept_min_forces' not in st.session_state:
    st.session_state['dept_min_forces'] = {1: 8, 2: 8, 3: 8} # עדכנתי מינימום ל-8 מתוך 20
if 'dept_schedules' not in st.session_state:
    st.session_state['dept_schedules'] = {}
if 'dept_config' not in st.session_state:
    st.session_state['dept_config'] = {
        1: {"format": "שבוע-שבוע", "start": datetime.now().date(), "end": (datetime.now() + timedelta(days=14)).date()},
        2: {"format": "חמשו\"ש", "start": datetime.now().date(), "end": (datetime.now() + timedelta(days=14)).date()},
        3: {"format": "שבוע-שבוע", "start": datetime.now().date(), "end": (datetime.now() + timedelta(days=14)).date()},
    }

def authenticate(username, password):
    users = st.session_state['users_db']
    if username in users and users[username]["pass"] == password:
        return users[username]
    return None

# --- מסך 1: התחברות והרשמה ---
def login_page():
    show_logo()
    st.markdown("<h1>MiluiMate - כניסה למערכת</h1>", unsafe_allow_html=True)
    
    tab_login, tab_signup = st.tabs(["🔑 התחברות למערכת", "📝 יצירת משתמש חדש"])
    
    with tab_login:
        with st.form("login_form"):
            st.markdown("### התחברות משתמש קיים")
            username = st.text_input("שם משתמש:")
            password = st.text_input("סיסמה:", type="password")
            submit = st.form_submit_button("התחבר למערכת")
            
            if submit:
                user = authenticate(username, password)
                if user:
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = user
                    st.rerun()
                else:
                    st.error("שם משתמש או סיסמה שגויים.")

    with tab_signup:
        with st.form("signup_form"):
            st.markdown("### רישום חייל חדש לפלוגה")
            new_username = st.text_input("בחר שם משתמש (באנגלית/מספרים לכניסה עתידית):")
            new_password = st.text_input("בחר סיסמה:", type="password")
            new_name = st.text_input("שם מלא (כפי שיופיע למפקד בטבלאות):")
            
            col_dept, col_role = st.columns(2)
            with col_dept:
                new_dept = st.selectbox("שיוך למחלקה:", [1, 2, 3])
            with col_role:
                new_role = st.selectbox("תפקיד / פק\"ל:", ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"])
            
            submit_signup = st.form_submit_button("➕ צור משתמש והתחבר אוטומטית")
            
            if submit_signup:
                if new_username in st.session_state['users_db']:
                    st.error("שם המשתמש כבר תפוס במערכת. אנא בחר שם משתמש אחר.")
                elif not new_username or not new_password or not new_name:
                    st.error("אנא מלא את כל השדות.")
                else:
                    st.session_state['users_db'][new_username] = {"pass": new_password, "role": "soldier", "name": new_name}
                    st.session_state['db_soldiers'][new_name] = {
                        "role": new_role, "department": new_dept,
                        "constraints": [{"סוג האילוץ": "אין לי העדפה", "פירוט / מלל חופשי": "זמין לסבב מחלקתי הוגן", "טווח תאריכים": "-", "דחיפות": "סבב רגיל", "סטטוס": "אושר"}]
                    }
                    st.session_state['logged_in'] = True
                    st.session_state['user_info'] = st.session_state['users_db'][new_username]
                    st.rerun()

# --- מסך 2: ממשק חייל ---
def soldier_page():
    show_logo()
    user_name = st.session_state['user_info']['name']
    st.markdown(f"<h2>שלום {user_name}, עדכן את אילוציך במערכת</h2>", unsafe_allow_html=True)
    
    with st.form("constraints_form"):
        st.markdown("### הגשת אילוץ חדש")
        
        curr_dept = st.session_state['db_soldiers'].get(user_name, {}).get("department", 1)
        curr_role = st.session_state['db_soldiers'].get(user_name, {}).get("role", "רובאי לוחם")
        roles_list = ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"]
        
        department = st.selectbox("מספר מחלקה (ניתן לעדכון):", [1, 2, 3], index=[1,2,3].index(curr_dept))
        role = st.selectbox("תפקיד בכוח / פק\"ל:", roles_list, index=roles_list.index(curr_role) if curr_role in roles_list else 8)
        
        request_type = st.selectbox("סוג האילוץ (סיווג דחיפות):", ["אין לי העדפה", "הליך רפואי", "אירוע משפחתי", "סיבה אישית", "מבחן/לימודים", "אחר"])
        free_text = st.text_input("פירוט האילוץ (מלל חופשי):", placeholder="הקלד כאן פרטים נוספים...")
        
        st.markdown("**בחר את טווח התאריכים המדויק לאילוץ זה:**")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("מתאריך:", datetime.now())
        with col_d2:
            end_date = st.date_input("עד תאריך (כולל):", datetime.now() + timedelta(days=2))
            
        submit_req = st.form_submit_button("➕ שלח וסנכרן ללוח המחלקה")
        
        if submit_req:
            if start_date > end_date and request_type != "אין לי העדפה":
                st.error("תאריך ההתחלה לא יכול להיות מאוחר מתאריך הסיום.")
            else:
                if request_type == "אין לי העדפה":
                    priority_tier = "סבב רגיל"
                    initial_status = "אושר"
                    formatted_range = "-"
                    text_detail = free_text if free_text else "זמין לסבב מחלקתי הוגן"
                else:
                    text_detail = free_text if free_text else "אין פירוט"
                    formatted_range = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
                    if request_type in ["הליך רפואי", "מבחן/לימודים"]:
                        priority_tier = "דרגה א' - קריטי"
                        initial_status = "אושר"
                    elif request_type in ["אירוע משפחתי", "סיבה אישית"]:
                        priority_tier = "דרגה ב' - בינוני"
                        initial_status = "בבדיקה"
                    else:
                        priority_tier = "דרגה ג' - נמוכה"
                        initial_status = "בבדיקה"

                new_constraint = {
                    "סוג האילוץ": request_type, "פירוט / מלל חופשי": text_detail,
                    "טווח תאריכים": formatted_range, "דחיפות": priority_tier, "סטטוס": initial_status
                }
                
                st.session_state['db_soldiers'][user_name]["constraints"] = [new_constraint]
                st.session_state['db_soldiers'][user_name]["role"] = role
                st.session_state['db_soldiers'][user_name]["department"] = department
                st.success(f"הנתונים נקלטו! סווג כ-{priority_tier} ומסונכרן למחלקה {department}.")

    my_constraints = st.session_state['db_soldiers'].get(user_name, {}).get("constraints", [])
    if my_constraints:
        st.markdown("### 📋 הסטטוס הפעיל שלך במערכת המשותפת:")
        st.table(pd.DataFrame(my_constraints))
        if st.button("🗑️ אפס סטטוס ל-'אין לי העדפה'"):
            st.session_state['db_soldiers'][user_name]["constraints"] = [{"סוג האילוץ": "אין לי העדפה", "פירוט / מלל חופשי": "זמין לסבב מחלקתי הוגן", "טווח תאריכים": "-", "דחיפות": "סבב רגיל", "סטטוס": "אושר"}]
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 התנתק מהמערכת"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- מסך 3: ממשק מפקד - מנוע חכם וטבלה צבעונית ---
def commander_page():
    show_logo()
    st.markdown("<h1>ניהול שיבוץ - MiluiMate</h1>", unsafe_allow_html=True)
    
    st.markdown("### 🗺️ מסוף פיקוד היררכי")
    selected_dept = st.selectbox("בחר מחלקה לניהול ושליטה (מחלקות 1, 2, או 3):", [1, 2, 3], index=0)
    st.markdown(f"<p style='color:#556644; font-weight:bold; text-align:right;'>מציג ועורך כעת נתונים בלעדיים עבור: מחלקה {selected_dept}</p>", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([" הגדרת דרישות", "🚦 סטטוס אילוצים", "📅 לוח יציאות דינמי"])
    
    with tab1:
        with st.form("commander_constraints_form"):
            st.markdown(f"### 🛠️ קביעת אילוצים קשיחים וטווח זמנים - מחלקה {selected_dept}")
            min_forces = st.number_input(f"סד\"כ לוחמים מינימלי חובה בבסיס ממחלקה {selected_dept}:", min_value=1, max_value=30, value=st.session_state['dept_min_forces'].get(selected_dept, 8))
            exit_format = st.selectbox("תבנית יציאות מועדפת למחלקה:", ["שבוע-שבוע", "חמשו\"ש", "יומי"])
            
            st.markdown("**📅 בחר טווח זמן לשיבוץ המערכת:**")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                t_start = st.date_input("מתאריך (תחילת תקופה):", st.session_state['dept_config'][selected_dept]["start"])
            with col_t2:
                t_end = st.date_input("עד תאריך (סיום תקופה):", st.session_state['dept_config'][selected_dept]["end"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            save_requirements = st.form_submit_button("💾 שמור דרישות מחלקה")
            if save_requirements:
                if t_start > t_end:
                    st.error("תאריך התחלת התקופה לא יכול להיות מאוחר מתאריך הסיום.")
                else:
                    st.session_state['dept_min_forces'][selected_dept] = min_forces
                    st.session_state['dept_config'][selected_dept] = {"format": exit_format, "start": t_start, "end": t_end}
                    st.success(f"הדרישות המבצעיות עבור מחלקה {selected_dept} נשמרו בהצלחה!")

    with tab2:
        st.markdown(f"### 🚦 בקרת אילוצי פרט - מחלקה {selected_dept}")
        rows = []
        for soldier_name, data in st.session_state['db_soldiers'].items():
            if data.get("department", 1) == selected_dept:
                c = data.get("constraints", [{}])[0] if data.get("constraints") else {}
                rows.append({
                    "שם החייל": soldier_name, "תפקיד / פק\"ל": data.get("role", "רובאי לוחם"),
                    "סוג הסטטוס/אילוץ": c.get("סוג האילוץ", "אין לי העדפה"),
                    "טווח תאריכים": c.get("טווח תאריכים", "-"),
                    "סיווג דחיפות": c.get("דחיפות", "סבב רגיל"), "סטטוס בקשה": c.get("סטטוס", "אושר")
                })
        
        if rows:
            df_feedback = pd.DataFrame(rows)
            df_feedback.insert(0, 'מס"ד', range(1, len(df_feedback) + 1))

            def color_rows(row):
                status_req = row["סוג הסטטוס/אילוץ"]
                status_approval = row["סטטוס בקשה"]
                if "אין לי העדפה" in status_req: return [''] * len(row)
                if status_approval == "אושר": return ['background-color: rgba(144, 238, 144, 0.4); color: black'] * len(row)
                elif status_approval == "לא אושר": return ['background-color: rgba(255, 182, 193, 0.5); color: black'] * len(row)
                elif status_approval == "בבדיקה": return ['background-color: rgba(255, 239, 204, 0.6); color: black'] * len(row)
                return [''] * len(row)

            styled_feedback = df_feedback.style.apply(color_rows, axis=1)
            st.dataframe(styled_feedback, use_container_width=True, hide_index=True)
            
            st.markdown("#### ✍️ שינוי ידני של סטטוס אילוץ:")
            dept_soldiers = [name for name, data in st.session_state['db_soldiers'].items() if data.get("department", 1) == selected_dept]
            col_sel1, col_sel2, col_sel3 = st.columns(3)
            with col_sel1:
                chosen_soldier = st.selectbox("בחר חייל מהמחלקה:", dept_soldiers)
            with col_sel2:
                new_status_choice = st.selectbox("קבע סטטוס חדש:", ["אושר", "לא אושר", "בבדיקה"])
            with col_sel3:
                st.markdown("<br>", unsafe_allow_html=True)
                if st.button("🔄 עדכן סטטוס"):
                    if st.session_state['db_soldiers'][chosen_soldier].get("constraints"):
                        st.session_state['db_soldiers'][chosen_soldier]["constraints"][0]["סטטוס"] = new_status_choice
                        st.success(f"הסטטוס של {chosen_soldier} עודכן!")
                        st.rerun()

    with tab3:
        cfg = st.session_state['dept_config'][selected_dept]
        req_min_forces = st.session_state['dept_min_forces'].get(selected_dept, 8)
        st.markdown(f"### 📅 לוח שיבוץ חכם: {cfg['start'].strftime('%d/%m')} עד {cfg['end'].strftime('%d/%m')}")
        
        sched_key = f'df_dept_{selected_dept}'
        
        if st.button(f"🚀 הפעל מנוע אופטימיזציה (סנכרון תאריכים מלא)"):
            with st.spinner(f"מחשב חפיפות תאריכים ובונה סד\"כ אופטימלי..."):
                time.sleep(1.5)
                
                # --- המנוע החכם: בניית הלוח על בסיס תאריכים ותבניות ---
                dept_names = [name for name, data in st.session_state['db_soldiers'].items() if data.get("department", 1) == selected_dept]
                dept_roles = [st.session_state['db_soldiers'][name].get("role", "רובאי לוחם") for name in dept_names]
                
                # יצירת מילון השיבוץ הריק
                schedule_dict = {name: {} for name in dept_names}
                
                # יצירת רשימת תאריכי היעד והעמודות
                date_list_cols = []
                curr_date = cfg['start']
                days_heb = ["ב'", "ג'", "ד'", "ה'", "ו'", "ש'", "א'"]
                
                while curr_date <= cfg['end']:
                    day_str = f"{curr_date.strftime('%d/%m')} ({days_heb[curr_date.weekday()]})"
                    date_list_cols.append((curr_date, day_str))
                    
                    # 1. שלב ראשון: בדיקת אילוצי חובה מאושרים לחייל
                    for name in dept_names:
                        c_list = st.session_state['db_soldiers'][name].get("constraints", [])
                        c = c_list[0] if c_list else {}
                        schedule_dict[name][day_str] = "נוכח בבסיס" # ברירת מחדל
                        
                        if c.get("סטטוס") == "אושר" and "אין לי העדפה" not in c.get("סוג האילוץ", ""):
                            c_start, c_end = parse_constraint_dates(c.get("טווח תאריכים", "-"))
                            if c_start and c_end and c_start <= curr_date <= c_end:
                                schedule_dict[name][day_str] = "בבית (חופשה)" # שחרור קשיח בגלל אילוץ
                    curr_date += timedelta(days=1)
                
                # 2. שלב שני: שיבוץ חיילים 'ללא העדפה' לפי תבנית סבב שבוע-שבוע/חמשושים
                for d_idx, (c_date, day_str) in enumerate(date_list_cols):
                    week_num = d_idx // 7
                    is_weekend = c_date.weekday() in [3, 4, 5] # חמישי, שישי, שבת
                    
                    for idx, name in enumerate(dept_names):
                        if schedule_dict[name][day_str] == "בבית (חופשה)":
                            continue # כבר משוחרר עקב אילוץ רפואי/מבחן
                            
                        c_list = st.session_state['db_soldiers'][name].get("constraints", [])
                        c = c_list[0] if c_list else {}
                        
                        # אם הוא ללא העדפה (פנוי לשיבוץ אלגוריתמי)
                        if "אין לי העדפה" in c.get("סוג האילוץ", "") or c.get("סטטוס") != "אושר":
                            is_team_a = (idx % 2 == 0)
                            if cfg['format'] == "שבוע-שבוע":
                                if week_num % 2 == 0:
                                    schedule_dict[name][day_str] = "נוכח בבסיס" if is_team_a else "בבית (חופשה)"
                                else:
                                    schedule_dict[name][day_str] = "בבית (חופשה)" if is_team_a else "נוכח בבסיס"
                            elif cfg['format'] == "חמשו\"ש":
                                if is_weekend:
                                    schedule_dict[name][day_str] = "בבית (חופשה)" if is_team_a else "נוכח בבסיס"
                                else:
                                    schedule_dict[name][day_str] = "נוכח בבסיס"
                
                # 3. שלב שלישי - המוח: אכיפת סד"כ מינימלי והחזרת לוחמים במקרה של חוסר חמור
                for c_date, day_str in date_list_cols:
                    present_count = sum(1 for n in dept_names if schedule_dict[n][day_str] == "נוכח בבסיס")
                    if present_count < req_min_forces:
                        shortage = req_min_forces - present_count
                        for name in dept_names:
                            if shortage <= 0: break
                            if schedule_dict[name][day_str] == "בבית (חופשה)":
                                # לא מחזירים לוחם שיש לו אילוץ מאושר קשיח, רק "ללא העדפה"
                                c_list = st.session_state['db_soldiers'][name].get("constraints", [])
                                is_hard_constraint = False
                                if c_list and c_list[0].get("סטטוס") == "אושר" and "אין לי העדפה" not in c_list[0].get("סוג האילוץ", ""):
                                    c_start, c_end = parse_constraint_dates(c_list[0].get("טווח תאריכים", "-"))
                                    if c_start and c_end and c_start <= c_date <= c_end:
                                        is_hard_constraint = True
                                
                                if not is_hard_constraint:
                                    schedule_dict[name][day_str] = "נוכח בבסיס" # מבטל יציאת סבב לטובת משימה
                                    shortage -= 1
                                    
                # הפיכת המילון החכם למסד נתונים של פנדס לתצוגה
                final_data = {"שם החייל": dept_names, "תפקיד / פק\"ל": dept_roles}
                for _, day_str in date_list_cols:
                    final_data[day_str] = [schedule_dict[name][day_str] for name in dept_names]
                    
                st.session_state['dept_schedules'][sched_key] = pd.DataFrame(final_data)
                st.success("השיבוץ הושלם: אילוצים הותאמו לתאריכים, בוצע סבב הוגן, ונסגרו חוסרי סד\"כ!")

        if sched_key in st.session_state['dept_schedules']:
            status_options = ["נוכח בבסיס", "בבית (חופשה)", "יציאה קצרה (כמה שעות)", "הארכת שהות (גיבוי)"]
            
            df_to_edit = st.session_state['dept_schedules'][sched_key].copy()
            df_to_edit.insert(0, 'מס"ד', range(1, len(df_to_edit) + 1))
            
            # יצירת קונפיגורציית dropdown לעמודות
            col_config_dict = {}
            dynamic_cols = [c for c in df_to_edit.columns if c not in ['מס"ד', 'שם החייל', 'תפקיד / פק"ל']]
            for col in dynamic_cols:
                col_config_dict[col] = st.column_config.SelectboxColumn(options=status_options, width="medium")
            
            # 🚨 הפעלת צבעים על הטבלה (Pandas Styling + Data Editor) 🚨
            def style_editor(val):
                return color_schedule(val)

            # כדי לאפשר עריכה צבעונית בסטרימליט, מעבירים את הסטיילר ל-data_editor
            styled_df = df_to_edit.style.map(style_editor, subset=dynamic_cols)
            
            edited_df = st.data_editor(
                styled_df,
                use_container_width=False,
                num_rows="fixed",
                key=f"editor_dept_{selected_dept}_colored",
                hide_index=True,
                column_config=col_config_dict
            )
            st.session_state['dept_schedules'][sched_key] = edited_df.drop(columns=['מס"ד'])

            st.markdown("#### 🧮 מחשבון בקרה מבצעי למחלקה:")
            st.markdown(f"**בקרת עמידה ביעד סד\"כ (מינימום נדרש: {req_min_forces}):**")
            calc_cols = st.columns(min(len(dynamic_cols), 5))
            for idx, day in enumerate(dynamic_cols[:5]):
                with calc_cols[idx]:
                    present_count = edited_df[day].isin(["נוכח בבסיס", "הארכת שהות (גיבוי)"]).sum()
                    if present_count >= req_min_forces:
                        st.success(f"**{day}** \n🟢 {present_count}/{req_min_forces}")
                    else:
                        st.error(f"**{day}** \n🔴 {present_count}/{req_min_forces}")

            if st.button("💾 שמור ונעל לוח זמנים ארוך טווח"):
                st.success("הלוח הדינמי המלא ננעל ונשמר בשרת בהצלחה!")

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

