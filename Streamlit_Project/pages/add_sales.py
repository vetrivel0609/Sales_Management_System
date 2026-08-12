import streamlit as st
import pandas as pd
from db import get_connection
from pages.add_payment import log_payment_page

def add_sales_page():

    st.title("📝 Operations Record Creator")

    tab1, tab2 = st.tabs([
        "Add New Sales Entry",
        "Log Payment Split Details"
    ])

    # =====================================
    # TAB 1 : ADD SALES
    # =====================================

    with tab1:

        conn = get_connection()

        role = st.session_state["role"]
        user_branch = st.session_state["branch"]

        # Load Branches
        if role == "Super Admin":

            branch_df = pd.read_sql(
                "SELECT branch_id, branch_name FROM branches",
                conn
            )

        else:

            branch_df = pd.read_sql(
                "SELECT branch_id, branch_name FROM branches WHERE branch_id=%s",
                conn,
                params=(user_branch,)
            )

        # Load Products (Course Names)
        product_df = pd.read_sql(
            """
            SELECT DISTINCT product_name
            FROM customer_sales
            ORDER BY product_name
            """,
            conn
        )

        conn.close()

        col1, col2 = st.columns(2)

        with col1:

            branch = st.selectbox(
                "Branch",
                branch_df["branch_name"]
            )

            customer = st.text_input("Customer Name")

            mobile = st.text_input("Mobile Number")

            # If no products exist yet, allow typing
            if product_df.empty:

                product = st.text_input("Course Name")

            else:

                product = st.selectbox(
                    "Course Name",
                    product_df["product_name"].tolist()
                )

        with col2:

            joining_date = st.date_input("Joining Date")

            gross_sales = st.number_input(
                "Gross Sales",
                min_value=0.0
            )

            status = st.selectbox(
                "Initial Status",
                [
                    "Open",
                    "Closed"
                ]
            )

        # =====================================
        # GENERATE SALE BUTTON
        # =====================================

        if st.button("Generate Sale", use_container_width=True):

            branch_id = int(
                branch_df.loc[
                    branch_df["branch_name"] == branch,
                    "branch_id"
                ].values[0]
            )

            conn = get_connection()
            cur = conn.cursor()

            cur.execute("""
                INSERT INTO customer_sales
                (
                    branch_id,
                    sale_date,
                    customer_name,
                    mobile_number,
                    product_name,
                    gross_sales,
                    received_amount,
                    status
                )
                VALUES
                (%s,%s,%s,%s,%s,%s,%s,%s)
            """,
            (
                branch_id,
                joining_date,
                customer,
                mobile,
                product,
                float(gross_sales),
                0,
                status
            ))

            conn.commit()

            cur.close()
            conn.close()

            st.success("✅ Sale created successfully!")

            st.rerun()

    # =====================================
    # TAB 2 : PAYMENT SPLIT
    # =====================================

    with tab2:
        log_payment_page()