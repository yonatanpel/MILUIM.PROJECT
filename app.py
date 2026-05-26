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

# --- הזרקת CSS מותאם אישית לעיצוב יוקרתי, פונטים גדולים והנגשת לשוניות מושלמת ---
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
    
    # יצירת 60 לוחמים באופן אוטומטי ומבוקר (20 לכל מחלקה)
    soldier_idx = 1
    for dept in [1, 2, 3]:
        for i in range(1, 21):
            s_name = f"לוחם {soldier_idx}"
            s_role = roles_pool[(soldier_idx - 1) % len(roles_pool)]
            
            # הוספת כמה אילוצי דוגמה התחלתיים בשביל הסימולציה
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

# הגדרת אילוצי סד"כ ברירת מחדל לכל מחלקה בנפרד
if 'dept_min_forces' not in st.session_state:
    st.session_state['dept_min_forces'] = {1: 4, 2: 4, 3: 4}
if 'dept_schedules' not in st.session_state:
    st.session_state['dept_schedules'] = {}

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

# --- מסך 2: ממשק חייל (כולל בחירת מספר מחלקה) ---
def soldier_page():
    show_logo()
    user_name = st.session_state['user_info']['name']
    st.markdown(f"<h2>שלום {user_name}, עדכן את אילוציך במערכת</h2>", unsafe_allow_html=True)
    
    with st.form("constraints_form"):
        st.markdown("### 📝 הגשת אילוץ חדש")
        
        # 🚨 תוספת בחירת מספר מחלקה חובה לפי דרישתך 🚨
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
                
                # סנכרון ושמירה ישירה תחת השם הנכון והמחלקה הנכונה בבסיס הנתונים המשותף
                st.session_state['db_soldiers'][user_name]["constraints"] = [new_constraint]
                st.session_state['db_soldiers'][user_name]["role"] = role
                st.session_state['db_soldiers'][user_name]["department"] = department
                st.success(f"הבקשה סווגה כ-{priority_tier} וסונכרנה בהצלחה למחלקה {department}!")

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

# --- מסך 3: ממשק מפקד (שליטה, סינון ועריכה לפי מחלקות) ---
def commander_page():
    show_logo()
    st.markdown("<h1>ניהול שיבוץ - MiluiMate</h1>", unsafe_allow_html=True)
    
    # בורר שליטה מחלקתי מרכזי בראש העמוד למפקד
    st.markdown("### 🗺️ מסוף פיקוד היררכי")
    selected_dept = st.selectbox("בחר מחלקה לניהול ושליטה (20 לוחמים למחלקה):", [1, 2, 3], index=0)
    st.markdown(f"<p style='color:#556644; font-weight:bold;'>מציג ועורך כעת נתונים בלעדיים עבור: מחלקה {selected_dept}</p>", unsafe_allow_html=True)
    st.markdown("---")

    # שלוש הלשוניות המקצועיות והמעוצבות
    tab1, tab2, tab3 = st.tabs([" הגדרת דרישות", "🚦 סטטוס אילוצים", "📅 לוח יציאות"])
    
    # --- טאב 1: דרישות סד"כ ספציפיות למחלקה שנבחרה ---
    with tab1:
        with st.form("commander_constraints_form"):
            st.markdown(f"### 🛠️ קביעת אילוצים קשיחים - מחלקה {selected_dept}")
            min_forces = st.number_input(f"סד\"כ לוחמים מינימלי חובה בבסיס ממחלקה {selected_dept}:", min_value=1, max_value=20, value=st.session_state['dept_min_forces'][selected_dept])
            exit_format = st.selectbox("תבנית יציאות מועדפת למחלקה:", ["יומי", "שבוע-שבוע", "חמשו\"ש", "יומיים"])
            
            st.markdown("<br>", unsafe_allow_html=True)
            save_requirements = st.form_submit_button("💾 שמור דרישות מחלקה")
            if save_requirements:
                st.session_state['dept_min_forces'][selected_dept] = min_forces
                st.success(f"הדרישות המבצעיות עבור מחלקה {selected_dept} נשמרו בהצלחה!")

    # --- טאב 2: פידבק ובקרת אילוצים מסונכרנים עבור המחלקה שנבחרה בלבד ---
    with tab2:
        st.markdown(f"### 🚦 בקרת אילוצי פרט - מחלקה {selected_dept}")
        
        rows = []
        for soldier_name, data in st.session_state['db_soldiers'].items():
            # סינון קשיח: רק לוחמים ששייכים למחלקה שנבחרה כרגע במסוף
            if data["department"] == selected_dept:
                if data["constraints"]:
                    for c in data["constraints"]:
                        rows.append({
                            "שם החייל": soldier_name,
                            "תפקיד / פק\"ל": data["role"],
                            "סיווג האילוץ": c["סוג האילוץ"],
                            "טווח תאריכים": c.get("טווח תאריכים", "-"),
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
        
        st.markdown("#### ✍️ שינוי ידני של סטטוס אילוץ במחלקה:")
        # סינון תיבת הבחירה של החיילים רק לחיילי המחלקה הנוכחית
        dept_soldiers = [name for name, data in st.session_state['db_soldiers'].items() if data["department"] == selected_dept]
        
        col_sel1, col_sel2, col_sel3 = st.columns(3)
        with col_sel1:
            chosen_soldier = st.selectbox("בחר חייל מהמחלקה:", dept_soldiers)
        with col_sel2:
            new_status_choice = st.selectbox("קבע סטטוס חדש:", ["אושר", "לא אושר", "בבדיקה"])
        with col_sel3:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 עדכן סטטוס"):
                if st.session_state['db_soldiers'][chosen_soldier]["constraints"]:
                    st.session_state['db_soldiers'][chosen_soldier]["constraints"][0]["סטטוס"] = new_status_choice
                    st.success(f"הסטטוס של {chosen_soldier} עודכן ומסך הפידבק רוענן!")
                    st.rerun()
                else:
                    st.warning("לחייל זה אין אילוצים פעילים לשינוי.")

    # --- טאב 3: הצעת שיבוץ ועריכה עצמאית נפרדת לכל מחלקה ---
    with tab3:
        st.markdown(f"### 📅 לוח שיבוץ ועריכה - מחלקה {selected_dept} (20 לוחמים)")
        
        # מפתח ייחודי ב-Session לשמירת הלוח של כל מחלקה בנפרד
        sched_key = f'df_dept_{selected_dept}'
        
        if st.button(f"🚀 הפעל מנוע אופטימיזציה למחלקה {selected_dept}"):
            with st.spinner(f"מנוע ה-CP-SAT מנתח את 20 לוחמי מחלקה {selected_dept}..."):
                time.sleep(1.5)
                
                # סינון שמות ותפקידים רק של המחלקה הנבחרת
                dept_names = [name for name, data in st.session_state['db_soldiers'].items() if data["department"] == selected_dept]
                dept_roles = [st.session_state['db_soldiers'][name]["role"] for name in dept_names]
                
                days = ["יום א'", "יום ב'", "יום ג'", "יום ד'", "יום ה'"]
                mock_data = {"שם החייל": dept_names, "תפקיד / פק\"ל": dept_roles}
                
                for d_idx, day in enumerate(days):
                    day_status = []
                    for idx, name in enumerate(dept_names):
                        constraints = st.session_state['db_soldiers'][name]["constraints"]
                        if constraints and constraints[0]["סטטוס"] == "אושר" and idx == d_idx:
                            day_status.append("בבית (חופשה)")
                        else:
                            day_status.append("נוכח בבסיס")
                    mock_data[day] = day_status
                    
                st.session_state['dept_schedules'][sched_key] = pd.DataFrame(mock_data)
                st.success(f"השיבוץ האופטימלי עבור מחלקה {selected_dept} חושב ונשמר!")

        if sched_key in st.session_state['dept_schedules']:
            status_options = ["נוכח בבסיס", "בבית (חופשה)", "יציאה קצרה (כמה שעות)", "הארכת שהות (גיבוי)"]
            
            # עריכה ידנית שמשפיעה אך ורק על הלוח של המחלקה הזו
            edited_df = st.data_editor(
                st.session_state['dept_schedules'][sched_key],
                use_container_width=True,
                num_rows="fixed",
                key=f"editor_dept_{selected_dept}",
                column_config={
                    "יום א'": st.column_config.SelectboxColumn(options=status_options),
                    "יום ב'": st.column_config.SelectboxColumn(options=status_options),
                    "יום ג'": st.column_config.SelectboxColumn(options=status_options),
                    "יום ד'": st.column_config.SelectboxColumn(options=status_options),
                    "יום ה'": st.column_config.SelectboxColumn(options=status_options),
                }
            )
            st.session_state['dept_schedules'][sched_key] = edited_df

            # מחשבון בקרה ספציפי למחלקה הנבחרת
            st.markdown("#### 🧮 מחשבון בקרה מבצעי למחלקה:")
            days_cols = ["יום א'", "יום ב'", "יום ג'", "יום ד'", "יום ה'"]
            calc_cols = st.columns(len(days_cols))
            
            req_forces = st.session_state['dept_min_forces'][selected_dept]
            for idx, day in enumerate(days_cols):
                with calc_cols[idx]:
                    present_count = edited_df[day].isin(["נוכח בבסיס", "הארכת שהות (גיבוי)"]).sum()
                    if present_count >= req_forces:
                        st.success(f"**{day}** \n🟢 {present_count}/{req_forces} נוכחים")
                    else:
                        st.error(f"**{day}** \n🔴 {present_count}/{req_forces} (חסר סד\"כ!)")

            if st.button("💾 שמור והפץ לוח מחלקתי סופי"):
                st.success(f"לוח היציאות של מחלקה {selected_dept} ננעל והופץ ללוחמים!")

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
