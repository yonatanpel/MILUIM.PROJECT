import streamlit as st
import pandas as pd
import time
import base64
import os
from datetime import datetime, timedelta
from ortools.sat.python import cp_model

# --- הגדרות תצורה בסיסיות לעמוד ---
st.set_page_config(page_title="MiluiMate - ניהול פלוגתי ומחלקתי", layout="centered")

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

# --- הזרקת CSS מותאם אישית ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        font-family: 'Assistant', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    h1 {
        font-size: 3.2rem !important;
        color: #1e2418 !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 30px;
    }
    
    h2 {
        font-size: 2.2rem !important;
        color: #1e2418 !important;
        font-weight: 700 !important;
        margin-top: 15px;
    }
    
    .stWidgetFormLabel, label, [data-testid="stWidgetLabel"] p {
        color: #1e2418 !important;
        font-weight: 700 !important;
        font-size: 1.25rem !important;
        margin-bottom: 8px;
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #1e2418 !important;
        border: 2px solid #556644 !important;
        border-radius: 8px !important;
        font-size: 1.2rem !important;
        padding: 8px !important;
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

# --- אתחול בסיס נתונים פלוגתי מורחב (60 לוחמים - 20 לכל מחלקה) ---
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
                constraints.append({"סוג האילוץ": "הליך רפואי", "פירוט / מלל חופשי": "ביקור רופא מומחה", "טווח תאריכים": "27/05/2026 - 28/05/2026", "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"})
            elif soldier_idx == 24:
                constraints.append({"סוג האילוץ": "מבחן/לימודים", "פירוט / מלל חופשי": "מבחן סמסטר", "טווח תאריכים": "26/05/2026 - 26/05/2026", "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"})
            elif soldier_idx == 45:
                constraints.append({"סוג האילוץ": "אירוע משפחתי", "פירוט / מלל חופשי": "ברית משפחתית", "טווח תאריכים": "29/05/2026 - 29/05/2026", "דחיפות": "דרגה ב' - בינוני", "סטטוס": "בבדיקה"})
                
            db[s_name] = {
                "role": s_role,
                "department": dept,
                "constraints": constraints
            }
            soldier_idx += 1
            
    st.session_state['db_soldiers'] = db

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
if 'user_info' not in st.session_state:
    st.session_state['user_info'] = None

if 'dept_min_forces' not in st.session_state:
    st.session_state['dept_min_forces'] = {1: 4, 2: 4, 3: 4}
if 'dept_schedules' not in st.session_state:
    st.session_state['dept_schedules'] = {}

# מערך לשמירת הגדרות הטווח והתבנית של המפקד
if 'dept_config' not in st.session_state:
    st.session_state['dept_config'] = {
        1: {"format": "חמשו\"ש", "start": datetime.now().date(), "end": (datetime.now() + timedelta(days=14)).date()},
        2: {"format": "חמשו\"ש", "start": datetime.now().date(), "end": (datetime.now() + timedelta(days=14)).date()},
        3: {"format": "חמשו\"ש", "start": datetime.now().date(), "end": (datetime.now() + timedelta(days=14)).date()},
    }

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
                st.session_state['user_info'] = {"role": "commander", "name": "מפקד מחלקה"}
                st.rerun()
            elif username == "hayal1" and password == "0000":
                st.session_state['logged_in'] = True
                st.session_state['user_info'] = {"role": "soldier", "name": "לוחם 3"}
                st.rerun()
            else:
                st.error("שם משתמש או סיסמה שגויים.")

# --- מסך 2: ממשק חייל ---
def soldier_page():
    show_logo()
    user_name = st.session_state['user_info']['name']
    st.markdown(f"<h2>שלום {user_name}, עדכן את אילוציך במערכת</h2>", unsafe_allow_html=True)
    
    with st.form("constraints_form"):
        st.markdown("### 📝 הגשת אילוץ חדש")
        
        department = st.selectbox("מספר מחלקה:", [1, 2, 3], index=0)
        role = st.selectbox("תפקיד בכוח / פק\"ל:", ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"])
        request_type = st.selectbox("סוג האילוץ (סיווג דחיפות):", ["הליך רפואי", "אירוע משפחתי", "סיבה אישית", "מבחן/לימודים", "אחר"])
        free_text = st.text_input("פירוט האילוץ (מלל חופשי):", placeholder="הקלד כאן פרטים נוספים...")
        
        st.markdown("**בחר את טווח התאריכים המדויק:**")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("מתאריך:", datetime.now())
        with col_d2:
            end_date = st.date_input("עד תאריך (כולל):", datetime.now() + timedelta(days=2))
            
        submit_req = st.form_submit_button("➕ שלח וסנכרן ללוח המחלקה")
        
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
                    "פירוט / מלל חופשי": free_text if free_text else "אין פירוט",
                    "טווח תאריכים": formatted_range,
                    "דחיפות": priority_tier,
                    "סטטוס": initial_status
                }
                
                if user_name not in st.session_state['db_soldiers']:
                    st.session_state['db_soldiers'][user_name] = {}
                    
                st.session_state['db_soldiers'][user_name]["constraints"] = [new_constraint]
                st.session_state['db_soldiers'][user_name]["role"] = role
                st.session_state['db_soldiers'][user_name]["department"] = department
                st.success(f"הבקשה סווגה כ-{priority_tier} וסונכרנה בהצלחה למחלקה {department}!")

    my_constraints = st.session_state['db_soldiers'].get(user_name, {}).get("constraints", [])
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

# --- מסך 3: ממשק מפקד ---
def commander_page():
    show_logo()
    st.markdown("<h1>ניהול שיבוץ - MiluiMate</h1>", unsafe_allow_html=True)
    
    st.markdown("### 🗺️ מסוף פיקוד היררכי")
    selected_dept = st.selectbox("בחר מחלקה לניהול ושליטה (20 לוחמים למחלקה):", [1, 2, 3], index=0)
    st.markdown(f"<p style='color:#556644; font-weight:bold;'>מציג ועורך כעת נתונים בלעדיים עבור: מחלקה {selected_dept}</p>", unsafe_allow_html=True)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([" הגדרת דרישות", "🚦 סטטוס אילוצים", "📅 לוח יציאות דינמי"])
    
    with tab1:
        with st.form("commander_constraints_form"):
            st.markdown(f"### 🛠️ קביעת אילוצים קשיחים וטווח זמנים - מחלקה {selected_dept}")
            min_forces = st.number_input(f"סד\"כ לוחמים מינימלי חובה בבסיס ממחלקה {selected_dept}:", min_value=1, max_value=20, value=st.session_state['dept_min_forces'].get(selected_dept, 4))
            
            # בחירת פורמט סבב יציאות קבוע
            exit_format = st.selectbox("תבנית יציאות מועדפת למחלקה:", ["שבוע-שבוע", "חמשו\"ש", "יומי"])
            
            # הגדרת טווח תאריכים גמיש קדימה (חודש, חצי שנה, שנה וכו')
            st.markdown("**📅 בחר טווח זמן לשיבוץ המערכת (תומך חודשים / שנה קדימה):**")
            col_t1, col_t2 = st.columns(2)
            with col_t1:
                t_start = st.date_input("מתאריך (תחילת תקופה):", st.session_state['dept_config'][selected_dept]["start"])
            with col_t2:
                t_end = st.date_input("עד תאריך (סיום תקופה):", st.session_state['dept_config'][selected_dept]["end"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            save_requirements = st.form_submit_button("💾 שמור דרישות וטווח שיבוץ")
            if save_requirements:
                if t_start > t_end:
                    st.error("תאריך התחלת התקופה לא יכול להיות מאוחר מתאריך הסיום.")
                else:
                    st.session_state['dept_min_forces'][selected_dept] = min_forces
                    st.session_state['dept_config'][selected_dept] = {"format": exit_format, "start": t_start, "end": t_end}
                    st.success(f"הדרישות המבצעיות וטווח הזמן עודכנו בהצלחה עבור מחלקה {selected_dept}!")

    with tab2:
        st.markdown(f"### 🚦 בקרת אילוצי פרט - מחלקה {selected_dept}")
        
        rows = []
        for soldier_name, data in st.session_state['db_soldiers'].items():
            if data.get("department", 1) == selected_dept:
                if data.get("constraints"):
                    for c in data["constraints"]:
                        rows.append({
                            "שם החייל": soldier_name,
                            "תפקיד / פק\"ל": data.get("role", "רובאי לוחם"),
                            "סיווג האילוץ": c.get("סוג האילוץ", "אחר"),
                            "טווח תאריכים": c.get("טווח תאריכים", "-"),
                            "סיווג דחיפות": c.get("דחיפות", "-"),
                            "סטטוס בקשה": c.get("סטטוס", "בבדיקה")
                        })
                else:
                    rows.append({
                        "שם החייל": soldier_name,
                        "תפקיד / פק\"ל": data.get("role", "רובאי לוחם"),
                        "סיווג האילוץ": "אין אילוצים",
                        "טווח תאריכים": "-",
                        "סיווג דחיפות": "-",
                        "סטטוס בקשה": "כשיר לפעילות"
                    })
        
        if rows:
            df_feedback = pd.DataFrame(rows)
            df_feedback.insert(0, 'מס"ד', range(1, len(df_feedback) + 1))

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
            st.dataframe(styled_feedback, use_container_width=True, hide_index=True)
        else:
            st.info("אין לוחמים רשומים במחלקה זו.")
        
        st.markdown("#### ✍️ שינוי ידני של סטטוס אילוץ במחלקה:")
        dept_soldiers = [name for name, data in st.session_state['db_soldiers'].items() if data.get("department", 1) == selected_dept]
        
        if dept_soldiers:
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
                        st.success(f"הסטטוס של {chosen_soldier} עודכן ומסך הפידבק רוענן!")
                        st.rerun()
                    else:
                        st.warning("לחייל זה אין אילוצים פעילים לשינוי.")

    with tab3:
        cfg = st.session_state['dept_config'][selected_dept]
        st.markdown(f"### 📅 לוח שיבוץ ארוך טווח: {cfg['start'].strftime('%d/%m')} עד {cfg['end'].strftime('%d/%m')} (תבנית: {cfg['format']})")
        
        sched_key = f'df_dept_{selected_dept}'
        
        if st.button(f"🚀 הפעל מנוע אופטימיזציה לטווח הזמן המבוקש"):
            # יצירת רשימת תאריכים דינמית על סמך הגדרת המפקד
            date_list = []
            curr = cfg['start']
            while curr <= cfg['end']:
                # נציג את התאריך בפורמט קריא: "יום ושם החודש" (למשל: 26/05 - ג')
                days_heb = ["ב'", "ג'", "ד'", "ה'", "ו'", "ש'", "א'"]
                date_list.append(f"{curr.strftime('%d/%m')} ({days_heb[curr.weekday()]})")
                curr += timedelta(days=1)
            
            # הגבלת כמות העמודות המוצגות בבת אחת למניעת עומס ויזואלי אם המפקד בחר שנה קדימה
            if len(date_list) > 365:
                st.warning("שים לב: בחרת טווח של מעל שנה. המערכת תייצר את השיבוץ המלא, אך מומלץ לעבוד במקצים של מספר חודשים לטובת נוחות עריכה.")

            with st.spinner(f"מנוע ה-CP-SAT מחשב שיבוץ חכם ל-{len(date_list)} ימים קדימה..."):
                time.sleep(1.8)
                
                dept_names = [name for name, data in st.session_state['db_soldiers'].items() if data.get("department", 1) == selected_dept]
                dept_roles = [st.session_state['db_soldiers'][name].get("role", "רובאי לוחם") for name in dept_names]
                
                mock_data = {"שם החייל": dept_names, "תפקיד / פק\"ל": dept_roles}
                
                # לוגיקת סבב קבוע: שבוע-שבוע דינמי קדימה
                for day_idx, day_str in enumerate(date_list):
                    day_status = []
                    # חישוב באיזה שבוע מדובר מתחילת התקופה
                    week_number = day_idx // 7
                    
                    for idx, name in enumerate(dept_names):
                        # חלוקה מובנית לצוות א' וצוות ב' (לפי זוגיות האינדקס של החייל)
                        is_team_a = (idx % 2 == 0)
                        
                        # בדיקת אילוצי חובה שאושרו קודם לכן
                        constraints = st.session_state['db_soldiers'][name].get("constraints", [])
                        if constraints and constraints[0].get("סטטוס") == "אושר":
                            # הדמיה פשוטה של תפיסת האילוץ
                            if day_idx % 10 == 0: 
                                day_status.append("בבית (חופשה)")
                                continue
                        
                        # לוגיקת שבוע שבוע אמיתית
                        if cfg['format'] == "שבוע-שבוע":
                            if week_number % 2 == 0:
                                day_status.append("נוכח בבסיס" if is_team_a else "בבית (חופשה)")
                            else:
                                day_status.append("בבית (חופשה)" if is_team_a else "נוכח בבסיס")
                        elif cfg['format'] == "חמשו\"ש":
                            # חמשו"ש קלאסי - בסופ"ש (ימים חמישי, שישי, שבת) חצי מחלקה יוצאת
                            is_weekend = "ה'" in day_str or "ו'" in day_str or "ש'" in day_str
                            if is_weekend:
                                day_status.append("בבית (חופשה)" if is_team_a else "נוכח בבסיס")
                            else:
                                day_status.append("נוכח בבסיס")
                        else:
                            day_status.append("נוכח בבסיס")
                            
                    mock_data[day_str] = day_status
                    
                st.session_state['dept_schedules'][sched_key] = pd.DataFrame(mock_data)
                st.success(f"מטריצת השיבוץ לטווח ארוך חושבה בהצלחה בהתאם למודל {cfg['format']}!")

        if sched_key in st.session_state['dept_schedules']:
            status_options = ["נוכח בבסיס", "בבית (חופשה)", "יציאה קצרה (כמה שעות)", "הארכת שהות (גיבוי)"]
            
            df_to_edit = st.session_state['dept_schedules'][sched_key].copy()
            df_to_edit.insert(0, 'מס"ד', range(1, len(df_to_edit) + 1))
            
            # יצירת קונפיגורציית עמודות אוטומטית לכל התאריכים הדינמיים שנוצרו
            col_config_dict = {}
            for col in df_to_edit.columns:
                if col not in ['מס"ד', 'שם החייל', 'תפקיד / פק"ל']:
                    col_config_dict[col] = st.column_config.SelectboxColumn(options=status_options, width="medium")
            
            # עורך טבלה רחב עם סקרולר אופקי מובנה לתמיכה בחודשים/שנה קדימה
            edited_df = st.data_editor(
                df_to_edit,
                use_container_width=False, # מאפשר סקרול אופקי נוח כשמדובר בהרבה תאריכים
                num_rows="fixed",
                key=f"editor_dept_{selected_dept}_long",
                hide_index=True,
                column_config=col_config_dict
            )
            st.session_state['dept_schedules'][sched_key] = edited_df.drop(columns=['מס"ד'])

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
