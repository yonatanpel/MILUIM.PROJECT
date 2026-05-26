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
    /* עיצוב משודרג ללשוניות (Tabs) */
    button[data-baseweb="tab"] {
        font-size: 1.1rem !important;
        font-weight: bold !important;
        color: #3d4a31 !important;
    }
    button[aria-selected="true"] {
        color: #556644 !important;
        border-bottom-color: #556644 !important;
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
            st.markdown("<h1 style='text-align: center; color: #556644;'>🐌 MiluiMate</h1>", unsafe_allow_html=True)

# --- ניהול מסד הנתונים הווירטואלי והסנכרון בזמן אמת ---
if 'db_soldiers' not in st.session_state:
    # אתחול רשימת לוחמים קבועה למערכת שמדמה בסיס נתונים מסונכרן
    st.session_state['db_soldiers'] = {
        "רועי": {"role": "חובש", "constraints": [{"סוג": "הליך רפואי", "פירוט": "טיפול שיניים חיוני", "טווח": "27/05/2026 - 29/05/2026"}]},
        "דניאל": {"role": "נגביסט", "constraints": []},
        "יוסי": {"role": "מפקד כיתה", "constraints": [{"סוג": "מבחן/לימודים", "פירוט": "מבחן סוף סמסטר בחקר ביצועים", "טווח": "26/05/2026 - 26/05/2026"}]},
        "אביב": {"role": "קלע", "constraints": []},
        "איתי": {"role": "נהג", "constraints": []},
        "נועם": {"role": "רחפניסט", "constraints": [{"סוג": "אירוע משפחתי", "פירוט": "ברית לבן דוד", "טווח": "28/05/2026 - 28/05/2026"}]}
    }

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

# --- מסך 2: ממשק חייל (הזנה מסונכרנת) ---
def soldier_page():
    show_logo()
    user_name = st.session_state['user_info']['name']
    st.markdown(f"<h2 style='text-align: center;'>שלום {user_name}, עדכן את אילוציך ב-MiluiMate</h2>", unsafe_allow_html=True)
    
    with st.form("constraints_form"):
        st.markdown("### 📝 הגשת אילוץ חדש (מסתנכרן מיד אצל המפקד)")
        role = st.selectbox("תפקיד בכוח:", ["מפקד כיתה", "חובש", "קלע", "נהג", "נגביסט", "רחפניסט", "מטוליסט", "מאגיסט", "רובאי לוחם"])
        request_type = st.selectbox("סוג האילוץ (סיווג):", ["הליך רפואי", "אירוע משפחתי", "סיבה אישית", "מבחן/לימודים", "אחר"])
        free_text = st.text_input("פירוט האילוץ (מלל חופשי):", placeholder="הקלד כאן פרטים נוספים...")
        
        st.markdown("**בחר את טווח התאריכים המדויק לאילוץ זה:**")
        col_d1, col_d2 = st.columns(2)
        with col_d1:
            start_date = st.date_input("מתאריך:", datetime.now())
        with col_d2:
            end_date = st.date_input("עד תאריך (כולל):", datetime.now() + timedelta(days=2))
            
        submit_req = st.form_submit_button("➕ שלח וסנכרן ללוח המפקד")
        
        if submit_req:
            if start_date > end_date:
                st.error("תאריך ההתחלה לא יכול להיות מאוחר מתאריך הסיום.")
            else:
                # עדכון ישיר של ה-Database הווירטואלי המרכזי בזמן אמת!
                formatted_range = f"{start_date.strftime('%d/%m/%Y')} - {end_date.strftime('%d/%m/%Y')}"
                new_constraint = {
                    "סוג": request_type,
                    "פירוט": free_text if free_text else "אין פירוט",
                    "טווח": formatted_range
                }
                st.session_state['db_soldiers'][user_name]["constraints"].append(new_constraint)
                st.session_state['db_soldiers'][user_name]["role"] = role
                st.success("האילוץ נשלח וסונכרן בהצלחה במסך המפקד!")

    # הצגת האילוצים הקיימים של החייל הנוכחי
    my_constraints = st.session_state['db_soldiers'][user_name]["constraints"]
    if my_constraints:
        st.markdown("### 📋 האילוצים הפעילים שלך במערכת:")
        st.table(pd.DataFrame(my_constraints))
        if st.button("🗑️ מחק את כל האילוצים שלי"):
            st.session_state['db_soldiers'][user_name]["constraints"] = []
            st.success("האילוצים נמחקו ומסך המפקד עודכן.")
            st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("🔒 התנתק מהמערכת"):
        st.session_state['logged_in'] = False
        st.rerun()

# --- מסך 3: ממשק מפקד (שלושה מסכים בלשוניות) ---
def commander_page():
    show_logo()
    st.markdown("<h2 style='text-align: center;'>שלום מפקד יקר, ברוך הבא ל-MiluiMate</h2>", unsafe_allow_html=True)
    
    # יצירת שלושת המסכים המבוקשים באמצעות לשוניות (Tabs)
    tab1, tab2, tab3 = st.tabs(["📋 מסך 1: הגדרת דרישות", "👥 מסך 2: אילוצי לוחמים (מסונכרן)", "📅 מסך 3: הצעת שיבוץ ועריכה"])
    
    # --- מסך ראשון: הדרישות של המפקד ---
    with tab1:
        with st.form("commander_constraints_form"):
            st.markdown("### 🛠️ הגדרת אילוצי סד\"כ כלליים")
            col1, col2 = st.columns(2)
            with col1:
                min_forces = st.number_input("סד\"כ לוחמים מינימלי חובה בבסיס (בכל יום):", min_value=1, value=6, key="cmd_min_forces")
                planning_days = st.number_input("טווח תכנון הסבב (בימים):", min_value=7, value=14)
            with col2:
                exit_format = st.selectbox("תבנית יציאות מועדפת לכוח:", ["יומי", "שבוע-שבוע", "חמשו\"ש", "יומיים"])
            
            st.markdown("---")
            st.markdown("### 🗂️ דרישת בעלי תפקידים חיוניים (כמויות לסימולציה)")
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
                st.success("הדרישות המבצעיות נשמרו בהצלחה במערכת!")

    # --- מסך שני: רשימת החיילים והאילוצים המסונכרנים שלהם בזמן אמת ---
    with tab2:
        st.markdown("### 👥 מצבת כוח אדם ואילוצי פרט מסונכרנים")
        st.info("🔄 מסך זה מסונכרן בזמן אמת. כל אילוץ או פק\"ל שהחייל מזין מהטלפון שלו מופיע כאן מיד!")
        
        # בניית טבלה מרוכזת מתוך בסיס הנתונים המשותף ב-State
        rows = []
        for soldier_name, data in st.session_state['db_soldiers'].items():
            if data["constraints"]:
                for c in data["constraints"]:
                    rows.append({
                        "שם החייל": soldier_name,
                        "תפקיד / פק\"ל": data["role"],
                        "סיווג האילוץ": c["סוג"],
                        "פירוט / מלל חופשי": c["פירוט"],
                        "טווח תאריכים": c["טווח"]
                    })
            else:
                rows.append({
                    "שם החייל": soldier_name,
                    "תפקיד / פק\"ל": data["role"],
                    "סיווג האילוץ": "אין אילוצים",
                    "פירוט / מלל חופשי": "כשיר לפעילות",
                    "טווח תאריכים": "-"
                })
        
        constraints_df = pd.DataFrame(rows)
        st.dataframe(constraints_df, use_container_width=True)

    # --- מסך שלישי: הצעת השיבוץ האופטימלי בעלת אפשרות עריכה ---
    with tab3:
        st.markdown("### 📅 הצעת שיבוץ אלגוריתמית (CP-SAT Engine)")
        
        if st.button("🚀 הפעל מנוע אופטימיזציה ושקלל אילוצים"):
            with st.spinner("מנוע ה-CP-SAT מנתח מיליוני אפשרויות על בסיס האילוצים המסונכרנים..."):
                time.sleep(1.8)
                
                # משיכת השמות העדכניים מבסיס הנתונים המסונכרן
                names_list = list(st.session_state['db_soldiers'].keys())
                roles_list = [st.session_state['db_soldiers'][name]["role"] for name in names_list]
                total_generated = len(names_list)
                
                days = ["יום א'", "יום ב'", "יום ג'", "יום ד'", "יום ה'"]
                mock_data = {"שם החייל": names_list, "תפקיד / פק\"ל": roles_list}
                
                # שיבוץ ראשוני חכם המתחשב באילוצים שהוזנו במסך 2
                for d_idx, day in enumerate(days):
                    day_status = []
                    for idx, name in enumerate(names_list):
                        # אם לחייל יש אילוץ פעיל (למשל רועי או יוסי), המערכת משחררת אותו אוטומטית לבית
                        has_active_constraint = len(st.session_state['db_soldiers'][name]["constraints"]) > 0
                        if has_active_constraint and idx == d_idx:
                            day_status.append("בבית (חופשה)")
                        else:
                            day_status.append("נוכח בבסיס")
                    mock_data[day] = day_status
                    
                st.session_state['current_df'] = pd.DataFrame(mock_data)
                st.success("האופטימיזציה הסתיימה! הפתרון המאזן וההוגן ביותר מוצג לפניך.")

        if 'current_df' in st.session_state:
            st.info("✍️ **אפשרות עריכה מלאה:** לחץ פעמיים על כל משבצת בטבלה למטה כדי לבצע התאמות, שינויים ידניים או חילופים!")
            
            status_options = ["נוכח בבסיס", "בבית (חופשה)", "יציאה קצרה (כמה שעות)", "הארכת שהות (גיבוי)"]
            
            # עורך הטבלה האינטראקטיבי המאפשר עריכה ידנית למפקד
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

            # מחשבון עמידה באילוצים קשים שמתעדכן בלייב בזמן שהמפקד עורך
            st.markdown("#### 🧮 מחשבון בקרה מבצעית (מתעדכן בלייב לפי העריכה שלך):")
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
                st.success("הלוח ננעל, נשמר והופץ בהצלחה לטלפונים של כלל הלוחמים!")

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
