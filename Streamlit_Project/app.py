import streamlit as st
from db import get_connection

from pages.dashboard import dashboard_page
from pages.add_sales import add_sales_page
from pages.sql_queries import sql_page

# ------------------------------------------------
# Page Configuration
# ------------------------------------------------

st.set_page_config(
    page_title="Student Enrollment Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Hide Streamlit sidebar

st.markdown("""
<style>

[data-testid="stSidebar"]{
    display:none;
}

[data-testid="collapsedControl"]{
    display:none;
}

</style>
""", unsafe_allow_html=True)


# ------------------------------------------------
# Login Function
# ------------------------------------------------

def login():

    st.markdown(
        "<h1 style='text-align:center;'>📊 Sales Management System</h1>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns([1,2,1])

    with c2:

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):

            conn = get_connection()

            cur = conn.cursor(dictionary=True)

            cur.execute("""
            SELECT *
            FROM users
            WHERE username=%s
            AND password=%s
            """, (username, password))

            user = cur.fetchone()

            conn.close()

            if user:

                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.session_state.role = user["role"]
                st.session_state.branch = user["branch_id"]
                st.session_state.page = "Dashboard"

                st.rerun()

            else:

                st.error("Invalid Username or Password")


# ------------------------------------------------
# Session State
# ------------------------------------------------

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"


# ------------------------------------------------
# LOGIN PAGE
# ------------------------------------------------

if not st.session_state.logged_in:

    login()

# ------------------------------------------------
# MAIN APPLICATION
# ------------------------------------------------

else:

    left, right = st.columns([1,4])

    with left:

        st.title("Navigation")

        if st.button("📊 Dashboard", use_container_width=True):
            st.session_state.page = "Dashboard"

        if st.button("📝 Operations Record Creator", use_container_width=True):
            st.session_state.page = "Operations"

        if st.session_state.role == "Super Admin":

            if st.button("💻 SQL Engine", use_container_width=True):
                st.session_state.page = "SQL"

        st.divider()

        st.write(f"👤 User : {st.session_state.username}")
        st.write(f"🔑 Role : {st.session_state.role}")

        st.divider()

        if st.button("Logout", use_container_width=True):

            st.session_state.clear()
            st.rerun()

    with right:

        if st.session_state.page == "Dashboard":
            dashboard_page()

        elif st.session_state.page == "Operations":

            add_sales_page()

        elif st.session_state.page == "SQL":

            sql_page()