import streamlit as st
import pandas as pd
import datetime
from db import get_connection


def log_payment_page():

    st.subheader("💰 Log Payment Split Details")

    conn = get_connection()

    role = st.session_state["role"]
    branch = st.session_state["branch"]

    # ==========================================
    # LOAD OPEN SALES
    # ==========================================

    query = """
    SELECT
        cs.sale_id,
        cs.branch_id,
        cs.customer_name,
        cs.product_name,
        cs.gross_sales,
        cs.received_amount,
        cs.pending_amount,
        cs.status,
        b.branch_name
    FROM customer_sales cs
    INNER JOIN branches b
        ON cs.branch_id = b.branch_id
    WHERE cs.status='Open'
    """

    params = []

    if role != "Super Admin":
        query += " AND cs.branch_id=%s"
        params.append(branch)

    query += " ORDER BY cs.sale_id"

    sales_df = pd.read_sql(
        query,
        conn,
        params=params
    )

    if sales_df.empty:

        st.success("🎉 No pending payments found.")

        conn.close()

        return

    # ==========================================
    # SALE DROPDOWN
    # ==========================================

    sales_df["display"] = (
        "ID "
        + sales_df["sale_id"].astype(str)
        + " - "
        + sales_df["customer_name"]
        + " ("
        + sales_df["product_name"]
        + ") - ₹"
        + sales_df["pending_amount"].astype(str)
        + " Pending"
    )

    selected_sale = st.selectbox(
        "Select Target Active Sale",
        sales_df["display"]
    )

    sale = sales_df[
        sales_df["display"] == selected_sale
    ].iloc[0]

    # ==========================================
    # SALE DETAILS
    # ==========================================

    c1, c2, c3 = st.columns(3)

    with c1:
        st.metric(
            "Gross Sales",
            f"₹ {sale['gross_sales']:,.2f}"
        )

    with c2:
        st.metric(
            "Received",
            f"₹ {sale['received_amount']:,.2f}"
        )

    with c3:
        st.metric(
            "Pending",
            f"₹ {sale['pending_amount']:,.2f}"
        )

    st.markdown("---")

    # ==========================================
    # PAYMENT DETAILS
    # ==========================================

    payment_method = st.selectbox(
        "Payment Collection Channel",
        [
            "Cash",
            "UPI",
            "Card",
            "Bank Transfer"
        ]
    )

    payment_amount = st.number_input(
        "Collected Split Amount (₹)",
        min_value=1.0,
        max_value=float(sale["pending_amount"]),
        step=1.0
    )

    payment_date = st.date_input(
        "Payment Date",
        value=datetime.date.today()
    )

    apply_payment = st.button(
        "Apply Payment Allocation",
        use_container_width=True,
        type="primary"
    )

    # ==========================================
    # SAVE PAYMENT
    # ==========================================

    if apply_payment:

        if payment_amount > float(sale["pending_amount"]):

            st.error("Payment amount cannot exceed pending amount.")

        else:

            cursor = conn.cursor()

            # ----------------------------------
            # Insert payment
            # ----------------------------------

            cursor.execute(
                """
                INSERT INTO payment_splits
                (
                    sale_id,
                    payment_date,
                    amount_paid,
                    payment_method
                )
                VALUES (%s,%s,%s,%s)
                """,
                (
                    int(sale["sale_id"]),
                    payment_date,
                    float(payment_amount),
                    payment_method
                )
            )

            # ----------------------------------
            # Calculate received amount
            # ----------------------------------

            new_received = (
                float(sale["received_amount"])
                + float(payment_amount)
            )

            if new_received >= float(sale["gross_sales"]):
                status = "Close"
            else:
                status = "Open"

            # ----------------------------------
            # Update customer_sales
            # ----------------------------------

            cursor.execute(
                """
                UPDATE customer_sales
                SET
                    received_amount=%s,
                    status=%s
                WHERE sale_id=%s
                """,
                (
                    new_received,
                    status,
                    int(sale["sale_id"])
                )
            )

            conn.commit()

            cursor.close()
            conn.close()

            st.success("✅ Payment recorded successfully.")

            st.rerun()