def commander_page():
    show_logo()
    st.markdown("<h1>ניהול שיבוץ - MiluiMate</h1>", unsafe_allow_html=True)
    
    st.markdown("### 🗺️ מסוף פיקוד היררכי")
    selected_dept = st.selectbox("בחר מחלקה לניהול ושליטה (מחלקות 1, 2, או 3):", [1, 2, 3], index=0)
    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([" הגדרת דרישות", "🚦 סטטוס אילוצים", "📅 לוח יציאות דינמי"])
    
    with tab1:
        # ... (השאירי את הגדרת הדרישות כמו שהיא) ...
        pass

    with tab2:
        st.markdown(f"### 🚦 בקרת אילוצי פרט - מחלקה {selected_dept}")
        
        # הצגת טבלה
        rows = []
        for soldier_name, data in st.session_state['db_soldiers'].items():
            if data.get("department", 1) == selected_dept:
                c = data.get("constraints", [{}])[0] if data.get("constraints") else {}
                rows.append({"שם החייל": soldier_name, "תפקיד / פק\"ל": data.get("role"), "סוג אילוץ": c.get("סוג האילוץ")})
        
        if rows:
            df = pd.DataFrame(rows)
            st.dataframe(df, use_container_width=True, hide_index=True)
        
        st.markdown("---")
        st.markdown("#### ✍️ ניהול חייל במחלקה:")
        dept_soldiers = [name for name, data in st.session_state['db_soldiers'].items() if data.get("department", 1) == selected_dept]
        
        if dept_soldiers:
            col_a, col_b = st.columns(2)
            with col_a:
                chosen_soldier = st.selectbox("בחר חייל לניהול:", dept_soldiers)
            with col_b:
                st.markdown("<br>", unsafe_allow_html=True)
                # כפתור מחיקה
                if st.button("🗑️ מחק חייל מהמחלקה", type="primary"):
                    del st.session_state['db_soldiers'][chosen_soldier]
                    # מחיקה גם ממאגר המשתמשים כדי שלא יוכל להתחבר
                    if chosen_soldier in [u_data['name'] for u_data in st.session_state['users_db'].values()]:
                        # חיפוש ומחיקה לפי שם
                        for u_key, u_data in list(st.session_state['users_db'].items()):
                            if u_data['name'] == chosen_soldier:
                                del st.session_state['users_db'][u_key]
                    
                    st.success(f"{chosen_soldier} נמחק בהצלחה מהמערכת!")
                    st.rerun()

    with tab3:
        # ... (השאירי את לוח היציאות הדינמי) ...
        pass
