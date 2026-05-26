import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# --- הגדרות עיצוב של הדף ---
st.set_page_config(page_title="סבב הוגן - ניהול סד''כ", layout="wide")

# --- יצירת/חיבור בסיס הנתונים (SQLite) ---
DB_NAME = "miluim_database.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # יצירת טבלת חיילים במידה ולא קיימת
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soldiers (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    # יצירת טבלת אילוצים במידה ולא קיימת
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

# --- פונקציות עזר לעבודה מול בסיס הנתונים ---
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

# --- יצירת טווח תאריכים ל-7 הימים הקרובים ---
start_date = datetime.today().date()
date_range = [str(start_date + timedelta(days=i)) for i in range(7)]

# --- כותרת ראשית ---
st.title("🎖️ מערכת 'סבב הוגן' - ניהול סד''כ ויציאות")
st.write("---")

# --- תפריט ניווט צידי ---
st.sidebar.header("תפריט ניווט")
app_mode = st.sidebar.radio("עבור אל:", ["👤 ממשק חייל (הזנת אילוצים)", "📋 ממשק מפקד - ניהול סד''כ", "🚀 הרצת אופטימיזציה"])

# ==========================================
# 1. ממשק חייל
# ==========================================
if app_mode == "👤 ממשק חייל (הזנת אילוצים)":
    st.header("אזור חייל - הזנת אילוצים לסבב הקרוב")
    
    soldiers_df = get_all_soldiers()
    
    if soldiers_df.empty:
        st.warning("⚠️ אין עדיין חיילים במערכת. על המפקד להזין חיילים בלשונית הניהול תחילה.")
    else:
        soldier_names = soldiers_df["name"].tolist()
        selected_soldier = st.selectbox("בחר את שמך מהרשימה:", soldier_names)
        
        st.subheader(f"בחר ימי אילוץ עבור: {selected_soldier}")
        st.write("סמן את הימים שבהם יש לך אילוץ קשיח (לימודים, מבחן, אירוע דחוף) שמונע ממך להישאר בבסיס:")
        
        selected_days = []
        for date_str in date_range:
            # הפיכת התאריך לשם היום בעברית
            day_name = pd.to_datetime(date_str).day_name()
            days_heb = {'Sunday': 'ראשון', 'Monday': 'שני', 'Tuesday': 'שלישי', 'Wednesday': 'רביעי', 'Thursday': 'חמישי', 'Friday': 'שישי', 'Saturday': 'שבת'}
            heb_day = days_heb.get(day_name, day_name)
            
            if st.checkbox(f"יום {heb_day} ({date_str})"):
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
        st.subheader("הוספת חייל חדש למחלקה/פלוגה")
        col1, col2 = st.columns(2)
        with col1:
            new_name = st.text_input("שם מלא של החייל:")
        with col2:
            new_role = st.selectbox("פק''ל / תפקיד:", ["לוחם", "מפקד", "חובש", "מטוליסט", "קלע"])
            
        if st.button("הוסף חייל לצוות"):
            if new_name:
                add_soldier(new_name, new_role)
                st.success(f"החייל {new_name} הוגדר בהצלחה כ-{new_role}!")
                st.rerun()
            else:
                st.error("חובה להזין שם חייל")
                
        st.write("---")
        st.subheader("חיילים רשומים כרגע במחלקה:")
        soldiers_df = get_all_soldiers()
        if not soldiers_df.empty:
            st.dataframe(soldiers_df[["name", "role"]].rename(columns={"name": "שם", "role": "תפקיד"}), use_container_width=True)
        else:
            st.info("אין עדיין חיילים רשומים.")

    with tab2:
        st.subheader("דרישות מינימום מבצעיות בבסיס")
        st.number_input("מינימום לוחמים נדרש בבסיס בכל יום נתון:", min_value=1, value=3, key="min_soldiers")
        st.checkbox("חובה לפחות מפקד אחד בבסיס בכל יום", value=True, key="req_commander")
        st.checkbox("חובה לפחות חובש אחד בבסיס בכל יום", value=True, key="req_medic")
        st.success("ההגדרות המבצעיות נשמרו בהצלחה.")

# ==========================================
# 3. הרצת אופטימיזציה
# ==========================================
elif app_mode == "🚀 הרצת אופטימיזציה":
    st.header("מנוע שיבוץ - יצירת לו''ז יציאות")
    
    soldiers_df = get_all_soldiers()
    constraints_df = get_all_constraints()
    
    if soldiers_df.empty:
        st.error("אין חיילים במערכת. לא ניתן לייצר לו''ז. עבור ללשונית מפקד והוסף חיילים.")
    else:
        st.write("הנתונים מוכנים להרצה. המערכת תקרא את אילוצי החיילים ואת דרישות המפקד ותייצר שיבוץ אופטימלי.")
        
        with st.expander("צפייה באילוצים הגולמיים שהוזנו על ידי החיילים"):
            st.dataframe(constraints_df, use_container_width=True)
            
        if st.button("🚀 ג'נרט לו''ז יציאות אופטימלי", type="primary"):
            st.info("מחשב את הלו''ז הטוב ביותר...")
            
            # (בשלב הבא נחליף את זה באלגוריתם האמיתי של Google OR-Tools)
            output_records = []
            for _, row in soldiers_df.iterrows():
                soldier_name = row["name"]
                soldier_role = row["role"]
                record = {"שם": soldier_name, "תפקיד": soldier_role}
                
                for date_str in date_range:
                    has_constraint = not constraints_df[(constraints_df["soldier_name"] == soldier_name) & (constraints_df["date"] == date_str)].empty
                    if has_constraint:
                        record[date_str] = "🏡 בית (אילוץ)"
                    else:
                        record[date_str] = "⛺ בסיס"
                        
                output_records.append(record)
                
            st.success("🎉 הלו''ז נוצר בהצלחה!")
            res_df = pd.DataFrame(output_records)
            st.dataframe(res_df, use_container_width=True)
