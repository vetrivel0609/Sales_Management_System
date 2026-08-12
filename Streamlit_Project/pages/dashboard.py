import streamlit as st
import pandas as pd
import datetime
from db import get_connection


def dashboard_page():

    st.title("📊 Student Enrollment Dashboard")

    conn = get_connection()

    role = st.session_state["role"]
    branch = st.session_state["branch"]

    # ==========================================
    # SESSION STATE
    # ==========================================

    if "dashboard_filter" not in st.session_state:
        st.session_state.dashboard_filter = False

    # ==========================================
    # LOAD BRANCHS
    # ==========================================

    if role == "Super Admin":

        branch_df = pd.read_sql(
            """
            SELECT
                branch_id,
                branch_name
            FROM branches
            ORDER BY branch_name
            """,
            conn
        )

    else:

        branch_df = pd.read_sql(
    """
    SELECT
        branch_id,
        branch_name
    FROM branches
    WHERE branch_id=%s
    """,
    conn,
    params=(int(branch),)
)

    # ==========================================
    # LOAD PRODUCTS
    # ==========================================

    product_df = pd.read_sql(
        """
        SELECT DISTINCT product_name
        FROM customer_sales
        ORDER BY product_name
        """,
        conn
    )

    # ==========================================
    # FILTERS
    # ==========================================

    st.markdown("## 🔍 Filters")

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    with col1:

        if role == "Super Admin":

            selected_branch = st.selectbox(
                "Branch",
                ["All"] + branch_df["branch_name"].tolist()
            )

        else:

            selected_branch = st.selectbox(
                "Branch",
                branch_df["branch_name"].tolist(),
                disabled=True
            )

    with col2:

        selected_product = st.selectbox(
            "Product",
            ["All"] + product_df["product_name"].tolist()
        )

    with col3:

        from_date = st.date_input(
            "From Date",
            value=datetime.date.today()
        )

    with col4:

        to_date = st.date_input(
            "To Date",
            value=datetime.date.today()
        )

    with col5:

        st.write("")
        st.write("")

        apply_filter = st.button(
            "Apply Filter",
            use_container_width=True
        )

    with col6:

        st.write("")
        st.write("")

        clear_filter = st.button(
            "Clear Filters",
            use_container_width=True
        )

    # ==========================================
    # FILTER LOGIC
    # ==========================================

    if apply_filter:
        st.session_state.dashboard_filter = True

    if clear_filter:
        st.session_state.dashboard_filter = False
        st.rerun()

    # ==========================================
    # SQL QUERY
    # ==========================================

    query = """
    SELECT
        cs.*,
        b.branch_name
    FROM customer_sales cs
    INNER JOIN branches b
        ON cs.branch_id = b.branch_id
    WHERE 1=1
    """

    params = []

    if role != "Super Admin":

        query += """
        AND cs.branch_id=%s
        """

        params.append(branch)

    if st.session_state.dashboard_filter:

        if role == "Super Admin":

            if selected_branch != "All":

                branch_id = int(

                    branch_df.loc[
                        branch_df["branch_name"] == selected_branch,
                        "branch_id"
                    ].values[0]

                )

                query += """
                AND cs.branch_id=%s
                """

                params.append(branch_id)

        if selected_product != "All":

            query += """
            AND cs.product_name=%s
            """

            params.append(selected_product)

        query += """
        AND cs.sale_date BETWEEN %s AND %s
        """

        params.append(from_date)
        params.append(to_date)

    # ==========================================
    # LOAD DATA
    # ==========================================

    df = pd.read_sql(
        query,
        conn,
        params=params
    )

    conn.close()
        # ==========================================
    # FINANCIAL SUMMARY
    # ==========================================

    st.markdown("---")
    st.subheader("📈 Financial Summary")

    if df.empty:

        gross = 0
        received = 0
        pending = 0

    else:

        gross = float(df["gross_sales"].sum())
        received = float(df["received_amount"].sum())
        pending = float(df["pending_amount"].sum())

    c1, c2, c3 = st.columns(3)

    with c1:

        st.metric(
            "Overall Revenue",
            f"₹ {gross:,.2f}"
        )

    with c2:

        st.metric(
            "Received Amount",
            f"₹ {received:,.2f}"
        )

    with c3:

        st.metric(
            "Pending Amount",
            f"₹ {pending:,.2f}"
        )

    st.markdown("---")

    # ==========================================
    # CUSTOMER SALES REPORT
    # ==========================================

    st.subheader("📋 Customer Sales Report")

    if df.empty:

        st.warning("No records found.")

    else:

        display_df = df[
            [
                "sale_id",
                "branch_name",
                "sale_date",
                "customer_name",
                "mobile_number",
                "product_name",
                "gross_sales",
                "received_amount",
                "pending_amount",
                "status"
            ]
        ].copy()

        display_df.columns = [
            "Sale ID",
            "Branch",
            "Sale Date",
            "Customer Name",
            "Mobile Number",
            "Course Name",
            "Gross Sales",
            "Received Amount",
            "Pending Amount",
            "Status"
        ]

        st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True
        )