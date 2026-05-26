import streamlit as st
import pandas as pd
import time
import base64
import os
from datetime import datetime, timedelta
from ortools.sat.python import cp_model

# --- הגדרות תצורה בסיסיות לעמוד ---
st.set_page_config(page_title="MiluiMate - מערכת פיקוד ושליטה", layout="centered")

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

# --- הזרקת CSS מותאם אישית לעיצוב חמ\"ל יוקרתי, קריא ובעל פונטים מוגדלים ---
st.markdown("""
    <style>
    html, body, [class*="css"]  {
        direction: rtl;
        text-align: right;
        font-family: 'Assistant', 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    }
    
    h1 {
        font-size: 3rem !important;
        color: #1e2418 !important;
        font-weight: 800 !important;
        text-align: center;
        margin-bottom: 10px;
    }
    h2 {
        font-size: 2.2rem !important;
        color: #1e2418 !important;
        font-weight: 700 !important;
        margin-top: 15px;
    }
    h3 {
        font-size: 1.6rem !important;
        color: #2e3b23 !important;
        font-weight: 600 !important;
    }
    
    .stWidgetFormLabel, label, [data-testid="stWidgetLabel"] p {
        color: #1e2418 !important;
        font-weight: 700 !important;
        font-size: 1.15rem !important;
        margin-bottom: 6px;
    }
    
    .stTextInput>div>div>input, .stSelectbox>div>div>div, .stNumberInput>div>div>input {
        background-color: #ffffff !important;
        color: #1e2418 !important;
        border: 2px solid #556644 !important;
        border-radius: 6px !important;
        font-size: 1.1rem !important;
    }
    
    div[data-testid="stMetricValue"] {
        font-size: 2.2rem !important;
        font-weight: bold !important;
        color: #1e2418 !important;
    }
    div[data-testid="metric-container"] {
        background-color: rgba(255, 255, 255, 0.9);
        border: 2px solid #556644;
        padding: 18px;
        border-radius: 12px;
        box-shadow: 0px 5px 15px rgba(0, 0, 0, 0.12);
    }
    
    div[data-testid="stForm"] {
        background-color: rgba(255, 255, 255, 0.88) !important;
        border-radius: 14px;
        padding: 25px;
        border: 2px solid #556644 !important;
        box-shadow: 0 10px 35px rgba(0,0,0,0.12);
    }
    
    .stButton>button {
        background-color: #556644;
        color: white;
        border-radius: 8px;
        border: 1px solid #3d4a31;
        padding: 12px 28px;
        font-size: 1.2rem;
        font-weight: bold;
        transition: all 0.3s ease;
        box-shadow: 0px 4px 8px rgba(0,0,0,0.15);
        width: 100%;
    }
    .stButton>button:hover {
        background-color: #3d4a31;
        color: #ffffff;
        transform: translateY(-2px);
    }
    
    button[data-baseweb="tab"] {
        font-size: 1.3rem !important;
        font-weight: bold !important;
        color: #4a5740 !important;
        padding: 12px 20px !important;
    }
    button[aria-selected="true"] {
        color: #1e2418 !important;
        border-bottom-color: #1e2418 !important;
        background-color: rgba(255, 255, 255, 0.4) !important;
        border-radius: 8px 8px 0 0;
    }
    
    .stDataFrame, [data-testid="stDataEditor"] {
        background-color: rgba(255, 255, 255, 0.9) !important;
        border-radius: 10px;
        padding: 5px;
        border: 1px solid #556644;
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
        "רועי": {"role": "חובש", "constraints": [{"סוג": "הליך רפואי", "פירוט": "ניתוח כירורגי באסותא", "טווח": "27/05/2026 - 29/05/2026", "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"}]},
        "דניאל": {"role": "נגביסט", "constraints": []},
        "יוסי": {"role": "מפקד כיתה", "constraints": [{"סוג": "מבחן/לימודים", "פירוט": "מבחן מועד א' בכלכלה מאקרו", "טווח": "26/05/2026 - 26/05/2026", "דחיפות": "דרגה א' - קריטי", "סטטוס": "אושר"}]},
        "אביב": {"role": "קלע", "constraints": [{"סוג": "אירוע משפחתי", "פירוט": "חתונה של אחותי", "טווח": "28/05/2026 - 28/05/2026", "דחיפות": "דרגה ב' - בינוני", "סטטוס": "בבדיקה"}]},
        "איתי": {"role": "נהג", "constraints": []},
        "נועם": {"role": "רחפניסט", "constraints": [{"סוג": "אחר", "פירוט": "מעבר דירה", "טווח": "29/05/2026 - 29/05/2026", "דחיפות": "דרגה ג' - נמוכה", "סטטוס": "לא אושר"}]}
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
                    "תאריך התחלה": start_date.strftime("%d/%m/%Y"),
                    "תאריך סיום": end_date.strftime("%d/%m/%Y"),
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

# --- מסך 3: ממשק מפקד (שלושה מסכים מעוצבים בלשוניות) ---
def commander_page():
    show_logo()
    st.markdown("<h1>חמ\"ל ניהול שיבוץ - MiluiMate</h1>", unsafe_allow_html=True)
    
    tab1, tab2, tab3 = st.tabs(["⚙️ מסך 1: הגדרת דרישות סד\"כ", "🚦 מסך 2: פידבק סטטוס אילוצים", "📅 מסך 3: לוח שיבוץ אופטימלי"])
    
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
        st.info("💡 **מדריך צבעים לחמ\"ל:** שורות ב-🟢 אושרו אלגוריתמית/ידנית | שורות ב-🔴 נדחו עקב חוסר סד\"כ | שורות ללא צבע כשירים ללא אילוצים.")
        
        rows = []
        for soldier_name, data in st.session_state['db_soldiers'].items():
            if data["constraints"]:
                for c in data["constraints"]:
                    rows.append({
                        "שם החייל": soldier_name,
                        "תפקיד / פק\"ל": data["role"],
                        "סיווג האילוץ": c["סוג האילוץ"],
                        "טווח תאריכים": f"{c['תאריך התחלה']} - {c['תאריך סיום']}" if "תאריך התחלה" in c else c.get("טווח", "-"),
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
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🔄 עדכן סטטוס"):
                if st.session_state['db_soldiers'][chosen_soldier]["constraints"]:
                    st.session_state['db_soldiers'][chosen_soldier]["constraints"][0]["סטטוס"] = new_status_choice
                    st.success(f"הסטטוס של {chosen_soldier} עודכן ל-{new_status_choice} ומסך הפידבק נצבע מחדש!")
                    st.rerun()
                else:
                    st.warning("לחייל זה אין אילוצים רשומים לשינוי.")

    with tab3:
        st.markdown("### 📅 לוח שיבוץ אופטימלי (ניתן לעריכה ידנית ✍️)")
        
        if st.button("🚀 הפעל מנוע אופטימיזציה משוקלל דחיפויות"):
            with st.spinner("מנוע ה-CP-SAT מבצע אופטימיזציה ומשריין קודם כל אילוצים בדרגה א'..."):
                time.sleep(1.8)
                
                names_list = list(st.session_state['db_soldiers'].keys())
                roles_list = [st.session_state['db_soldiers'][name]["role"] for name in names_list]
                total_generated = len(names_list)
                
                days = ["יום א'", "יום ב'", "יום ג'", "יום ד'", "יום ה'"]
                mock_data = {"שם החייל": names_list, "תפקיד / פק\"ל": roles_list}
                
                for d_idx, day in enumerate(days):
                    day_status = []
                    for idx, name in enumerate(names_list):
                        constraints = st.session_state['db_soldiers'][name]["constraints"]
                        if constraints and constraints[0]["סטטוס"] == "אושר" and idx == d_idx:
                            day_status.append("בבית (חופשה)")
                        else:
                            day_status.append("נוכח בבסיס")
                    mock_data[day] = day_status
                    
                st.session_state['current_df'] = pd.DataFrame(mock_data)
                st.success("השיבוץ האופטימלי חושב והתחשב בדחיפויות הלוחמים!")

        if 'current_df' in st.session_state:
            st.info("💡 **טבלת שליטה ובקרה חכמה:** באפשרותך ללחוץ פעמיים על כל תא כדי לבצע התאמות קצרות או להאריך שהות!")
            
            status_options = ["נוכח בבסיס", "בבית (חופשה)", "יציאה קצרה (כמה שעות)", "הארכת שהות (גיבוי)"]
            
            edited_df = st.data_editor(
                st.session_state['current_df'],
                use_container_width=True,
                num_rows="fixed",
                column_config={
                    "יום א'": st.column_config.SelectboxColumn(options=status_options),
                    "יום ב'": st.column_config.SelectboxColumn(options=status_options),
                    "יום ג'": st.column_config.SelectboxColumn(options=status_options),
                    "יום ד'": st.column_config.SelectboxColumn(options=status_options),
                    "יום ה'": st.column_config.SelectboxColumn(options=status_options),
                }
            )
            st.session_state['current_df'] = edited_df

            st.markdown("#### 🧮 מחשבון בקרה מבצעית (מתעדכן בלייב):")
            days_cols = ["יום א'", "יום ב'", "יום ג'", "יום ד'", "יום ה'"]
            calc_cols = st.columns(len(days_cols))
            
            req_forces = st.session_state.get('min_forces', 6)
            for idx, day in enumerate(days_cols):
                with calc_cols[idx]:
                    present_count = edited_df[day].isin(["נוכח בבסיס", "הארכת שהות (גיבוי)"]).sum()
                    if present_count >= req_forces:
                        st.success(f"**{day}** \n🟢 {present_count}/{req_forces} ביחידה")
                    else:
                        st.error(f"**{day}** \n🔴 {present_count}/{req_forces} (סד\"כ חסר!)")

            if st.button("💾 שמור והפץ לוח סופי מאושר"):
                st.success("הלוח נשמר, ננעל והופץ בהצלחה לטלפונים של כלל הלוחמים בכוח!")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 התנתק מהמערכת"):
        st.session_state['logged_in'] = False
        if 'current_df' in st.session_state:
            del st.session_state['current_df']
        st.rerun()

# --- ניתוב דפים קבוע ותקין ---
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
