import streamlit as st
import pandas as pd
from db import get_connection


def sql_page():

    st.title("💻 Live SQL Business Analytics Engine")

    conn = get_connection()

    queries = {

"1. Retrieve all records from customer_sales":
"""
SELECT * FROM customer_sales;
""",

"2. Retrieve all records from branches":
"""
SELECT * FROM branches;
""",

"3. Retrieve all records from payment_splits":
"""
SELECT * FROM payment_splits;
""",

"4. Display all Open sales":
"""
SELECT *
FROM customer_sales
WHERE status='Open';
""",

"5. Retrieve all sales belonging to Chennai branch":
"""
SELECT cs.*
FROM customer_sales cs
JOIN branches b
ON cs.branch_id=b.branch_id
WHERE b.branch_name='Chennai';
""",

"6. Calculate Total Gross Sales":
"""
SELECT
SUM(gross_sales) AS Total_Gross_Sales
FROM customer_sales;
""",

"7. Calculate Total Received Amount":
"""
SELECT
SUM(received_amount) AS Total_Received
FROM customer_sales;
""",

"8. Calculate Total Pending Amount":
"""
SELECT
    b.branch_name AS Branch,
    cs.customer_name AS Customer,
    cs.pending_amount AS Pending_Amount
FROM customer_sales cs
JOIN branches b
    ON cs.branch_id = b.branch_id
WHERE cs.pending_amount > 0
ORDER BY b.branch_name, cs.customer_name;
""",

"9. Count Total Sales Per Branch":
"""
SELECT
b.branch_name,
COUNT(cs.sale_id) AS Total_Sales
FROM customer_sales cs
JOIN branches b
ON cs.branch_id=b.branch_id
GROUP BY b.branch_name;
""",

"10. Average Gross Sales":
"""
SELECT
AVG(gross_sales) AS Average_Gross_Sales
FROM customer_sales;
""",

"11. Sales Details with Branch Name":
"""
SELECT
cs.sale_id,
b.branch_name,
cs.customer_name,
cs.product_name,
cs.gross_sales
FROM customer_sales cs
JOIN branches b
ON cs.branch_id=b.branch_id;
""",

"12. Sales with Total Payment Received":
"""
SELECT
cs.sale_id,
cs.customer_name,
SUM(ps.amount_paid) AS Total_Paid
FROM customer_sales cs
LEFT JOIN payment_splits ps
ON cs.sale_id=ps.sale_id
GROUP BY cs.sale_id, cs.customer_name;
""",

"13. Branch-wise Total Gross Sales":
"""
SELECT
b.branch_name,
SUM(cs.gross_sales) AS Total_Gross
FROM customer_sales cs
JOIN branches b
ON cs.branch_id=b.branch_id
GROUP BY b.branch_name;
""",

"14. Sales Along with Payment Method":
"""
SELECT
cs.sale_id,
cs.customer_name,
ps.payment_method,
ps.amount_paid
FROM customer_sales cs
JOIN payment_splits ps
ON cs.sale_id=ps.sale_id;
""",

"15. Sales Along with Branch Admin":
"""
SELECT
cs.sale_id,
cs.customer_name,
b.branch_name,
u.username AS Branch_Admin
FROM customer_sales cs
JOIN branches b
ON cs.branch_id=b.branch_id
JOIN users u
ON b.branch_id=u.branch_id;
""",

"16. Pending Amount Greater than 5000":
"""
SELECT *
FROM customer_sales
WHERE pending_amount>5000;
""",

"17. Top 3 Highest Gross Sales":
"""
SELECT *
FROM customer_sales
ORDER BY gross_sales DESC
LIMIT 3;
""",

"18. Branch with Highest Gross Sales":
"""
SELECT
b.branch_name,
SUM(cs.gross_sales) AS Total_Gross
FROM customer_sales cs
JOIN branches b
ON cs.branch_id=b.branch_id
GROUP BY b.branch_name
ORDER BY Total_Gross DESC
LIMIT 1;
""",

"19. Monthly Sales Summary":
"""
SELECT
YEAR(sale_date) AS Year,
MONTH(sale_date) AS Month,
SUM(gross_sales) AS Total_Sales
FROM customer_sales
GROUP BY YEAR(sale_date), MONTH(sale_date);
""",

"20. Payment Method-wise Total Collection":
"""
SELECT
payment_method,
SUM(amount_paid) AS Total_Collection
FROM payment_splits
GROUP BY payment_method;
"""
}

    selected = st.selectbox(
        "Choose Query",list(queries.keys())
    )

    if st.button(
        "Execute Query",
        use_container_width=True,
        type="primary"
    ):

        try:

            df = pd.read_sql(
                queries[selected],
                conn
            )

            st.success("✅ Query executed successfully.")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True
            )

        except Exception as e:

            st.error(f"Error: {e}")

    conn.close()