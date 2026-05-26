import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from ortools.sat.python import cp_model

# --- 1. הגדרות עיצוב מתקדמות ועמוד רחב (Tactical Dark Theme) ---
st.set_page_config(page_title="סבב הוגן - ניהול סד''כ", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #0B1329 !important;
        color: #F8FAFC !important;
    }
    .stButton>button {
        border-radius: 20px !important;
        background-color: #111A30 !important;
        color: #F8FAFC !important;
        border: 2px solid #10B981 !important;
        padding: 8px 20px !important;
        font-weight: bold !important;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background-color: #10B981 !important;
        color: #0B1329 !important;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }
    header, footer, #MainMenu {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

# --- 2. ניהול בסיס הנתונים (SQLite) ---
DB_NAME = "miluim_database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soldiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS constraints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            soldier_name TEXT NOT NULL,
            date TEXT NOT NULL,
            UNIQUE(soldier_name, date)
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# --- 3. פונקציות עזר לבסיס הנתונים ---
def get_all_soldiers():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM soldiers", conn)
    conn.close()
    return df

def add_soldier(name, role):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO soldiers (name, role) VALUES (?, ?)", (name, role))
        conn.commit()
    except Exception as e:
        st.error(f"שגיאה בהוספת חייל: {e}")
    finally:
        conn.close()

def save_constraint(soldier_name, date_str):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT OR IGNORE INTO constraints (soldier_name, date) VALUES (?, ?)", (soldier_name, date_str))
        conn.commit()
    except Exception as e:
        st.error(f"שגיאה בשמירת אילוץ: {e}")
    finally:
        conn.close()

def clear_soldier_constraints(soldier_name):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM constraints WHERE soldier_name = ?", (soldier_name,))
    conn.commit()
    conn.close()

def get_all_constraints():
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM constraints", conn)
    conn.close()
    return df

# --- 4. הגדרת טווח תאריכים ---
start_date = datetime.today().date()
date_range = [str(start_date + timedelta(days=i)) for i in range(7)]

# --- 5. תפריט ניווט צידי מעוצב עם לוגו השבלול המקורי ---
with st.sidebar:
    st.markdown("""
        <div style="text-align: center;">
            <img src="http://googleusercontent.com/image_collection/image_retrieval/11864997502639120532" 
                 style="border-radius: 50%; width: 100px; height: 100px; object-fit: cover; border: 2px solid #10B981; background-color: white; padding: 5px;">
        </div>
    """, unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center; color: #10B981;'>ניהול סד\"כ</h3>", unsafe_allow_html=True)
    st.divider()
    
    app_mode = st.radio("עבור אל:", [
        "👤 ממשק חייל (הזנת אילוצים)", 
        "📋 ממשק מפקד - ניהול סד''כ", 
        "🚀 הרצת אופטימיזציה"
    ])
    st.divider()
    soldiers_count = len(get_all_soldiers())
    st.metric(label="חיילים רשומים בסגל הפלוגה", value=f"{soldiers_count} לוחמים")

# ==========================================
# 1. ממשק חייל (הזנת אילוצים)
# ==========================================
if app_mode == "👤 ממשק חייל (הזנת אילוצים)":
    st.header("אזור חייל - הזנת אילוצים לסבב הקרוב")
    
    soldiers_df = get_all_soldiers()
    
    if soldiers_df.empty:
        st.warning("אין עדיין חיילים במערכת. על המפקד להזין חיילים בלשונית הניהול תחילה.")
    else:
        soldier_names = soldiers_df["name"].tolist()
        selected_soldier = st.selectbox("בחר את שמך מהרשימה לביצוע הזדהות:", soldier_names)
        
        current_role = soldiers_df[soldiers_df["name"] == selected_soldier]["role"].values[0]
        st.info(f"מזוהה במערכת עם פק\"ל: **{current_role}**")
        
        st.write("---")
        st.subheader("סמן את ימי האילוץ שלך:")
        
        selected_days = []
        for date_str in date_range:
            day_name = pd.to_datetime(date_str).day_name()
            days_heb = {'Sunday': 'ראשון', 'Monday': 'שני', 'Tuesday': 'שלישי', 'Wednesday': 'רביעי', 'Thursday': 'חמישי', 'Friday': 'שישי', 'Saturday': 'שבת'}
            heb_day = days_heb.get(day_name, day_name)
            
            if st.checkbox(f"יום {heb_day} ({date_str})", key=f"date_{date_str}"):
                selected_days.append(date_str)
        
        if st.button("שמור אילוצים במערכת", type="primary"):
            clear_soldier_constraints(selected_soldier)
            for date_str in selected_days:
                save_constraint(selected_soldier, date_str)
            st.success(f"האילוצים של {selected_soldier} נשמרו בהצלחה!")

# ==========================================
# 2. ממשק מפקד - ניהול סד"כ
# ==========================================
elif app_mode == "📋 ממשק מפקד - ניהול סד''כ":
    st.header("אזור מפקד - ניהול כוח אדם ודרישות קשיחות")
    
    tab1, tab2 = st.tabs(["👥 ניהול רשימת חיילים", "⚙️ הגדרת אילוצי בסיס"])
    
    with tab1:
        st.subheader("הוספת חייל חדש וקביעת פק\"ל")
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("שם מלא של החייל:")
        with col2:
            new_role = st.selectbox("בחירת פק\"ל מחייב:", [
                "מאג", "נגב", "חובש", "מטול", "קלע", "רחפניסט", "מפקד", "לוחם"
            ])
            
        if st.button("הוסף חייל לצוות", use_container_width=True):
            if new_name:
                add_soldier(new_name, new_role)
                st.success(f"החייל {new_name} הוגדר בהצלחה עם פק\"ל {new_role}!")
                st.rerun()
            else:
                st.error("חובה להזין שם חייל")
                
        st.write("---")
        st.subheader("חיילים רשומים במחלקה:")
        
        soldiers_df = get_all_soldiers()
        if not soldiers_df.empty:
            for _, row in soldiers_df.iterrows():
                with st.container(border=True):
                    c_name, c_role, c_spacer = st.columns([3, 2, 5])
                    with c_name:
                        st.markdown(f"**👤 {row['name']}**")
                    with c_role:
                        st.markdown(f"פק\"ל: `{row['role']}`")
        else:
            st.info("אין עדיין חיילים רשומים.")

    with tab2:
        st.subheader("דרישות מינימום מבצעיות בבסיס")
        st.number_input("מינימום לוחמים נדרש בבסיס בכל יום נתון:", min_value=1, value=3, key="min_soldiers")
        st.checkbox("חובה לפחות מפקד אחד בבסיס בכל יום", value=True, key="req_commander")
        st.checkbox("חובה לפחות חובש אחד בבסיס בכל יום", value=True, key="req_medic")

# ==========================================
# 3. הרצת אופטימיזציה (מנוע CP-SAT האמיתי)
# ==========================================
elif app_mode == "🚀 הרצת אופטימיזציה":
    st.header("מנוע שיבוץ מתמטי - Google OR-Tools CP-SAT")
    
    soldiers_df = get_all_soldiers()
    constraints_df = get_all_constraints()
    
    if soldiers_df.empty:
        st.error("אין חיילים במערכת. לא ניתן לייצר לו''ז.")
    else:
        st.write("מנוע האופטימיזציה יחשב כעת את השיבוץ האופטימלי שמקיים את כל החוקים הקשיחים.")
        
        if st.button("🚀 הרץ פותר אילוצים מתמטי", type="primary", use_container_width=True):
            with st.spinner("מנוע CP-SAT פותר את משוואת השיבוץ ומאזן עומסים..."):
                
                # --- בניית מודל ה-CP-SAT ---
                model = cp_model.CpModel()
                
                num_soldiers = len(soldiers_df)
                num_days = len(date_range)
                
                # יצירת משתני החלטה: האם חייל s נמצא בבסיס ביום d
                # 1 = בבסיס, 0 = בבית
                x = {}
                for s in range(num_soldiers):
                    for d in range(num_days):
                        x[s, d] = model.NewBoolVar(f'x_{s}_{d}')
                
                # הגדרת חוקים קשיחים (Hard Constraints)
                for d in range(num_days):
                    date_str = date_range[d]
                    
                    # 1. דרישת מינימום לוחמים בבסיס בכל יום
                    model.Add(sum(x[s, d] for s in range(num_soldiers)) >= st.session_state.min_soldiers)
                    
                    # 2. חובת מפקד בבסיס
                    if st.session_state.req_commander:
                        model.Add(sum(x[s, d] for s in range(num_soldiers) if soldiers_df.iloc[s]['role'] == 'מפקד') >= 1)
                        
                    # 3. חובת חובש בבסיס
                    if st.session_state.req_medic:
                        model.Add(sum(x[s, d] for s in range(num_soldiers) if soldiers_df.iloc[s]['role'] == 'חובש') >= 1)
                
                # 4. חסימת ימי אילוץ (אם חייל סימן אילוץ, הוא חייב להיות בבית = 0)
                for s in range(num_soldiers):
                    s_name = soldiers_df.iloc[s]['name']
                    for d in range(num_days):
                        date_str = date_range[d]
                        is_blocked = not constraints_df[(constraints_df["soldier_name"] == s_name) & (constraints_df["date"] == date_str)].empty
                        if is_blocked:
                            model.Add(x[s, d] == 0)
                
                # פונקציית מטרה: מקסום הוגנות (שאיפה לחלק את ימי הבסיס והבית בצורה שווה ככל הניתן)
                # בשלב זה המודל שואף למקסם את ימי הבית האפשריים תחת המגבלות
                model.Maximize(sum(1 - x[s, d] for s in range(num_soldiers) for d in range(num_days)))
                
                # הרצת הפותר (Solver)
                solver = cp_model.CpSolver()
                status = solver.Solve(model)
                
                # הצגת תוצאות
                if status == cp_model.OPTIMAL or status == cp_model.FEASIBLE:
                    st.success("🎉 נמצא פתרון שיבוץ אופטימלי העומד בכל חוקי הסד\"כ והפק\"לים!")
                    
                    output_records = []
                    for s in range(num_soldiers):
                        s_name = soldiers_df.iloc[s]['name']
                        s_role = soldiers_df.iloc[s]['role']
                        record = {"שם": s_name, "פק\"ל": s_role}
                        
                        for d in range(num_days):
                            date_str = date_range[d]
                            if solver.Value(x[s, d]) == 1:
                                record[date_str] = "⛺ בסיס"
                            else:
                                record[date_str] = "🏡 בית"
                        output_records.append(record)
                        
                    res_df = pd.DataFrame(output_records)
                    st.dataframe(res_df, use_container_width=True)
                else:
                    st.error("❌ לא ניתן למצוא שיבוץ חוקי! דרישות המפקד מתנגשות עם אילוצי החיילים בשטח. שנה את הדרישות או פתח אילוצים.")
