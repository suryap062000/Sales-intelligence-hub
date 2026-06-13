import streamlit as st
from login import login
from sales import add_sale
from payments import add_payment
from db import get_connection

st.set_page_config(
    page_title="Sales Intelligence Hub",
    layout="wide"
)

# Session Initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# Login Screen
if not st.session_state.logged_in:

    st.title("Sales Intelligence Hub")
    st.subheader("Login")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):

        user = login(username, password)

        if user:

            st.session_state.logged_in = True
            st.session_state.user_id = user[0]
            st.session_state.username = user[1]
            st.session_state.role = user[4]
            st.session_state.branch_id = user[3]

            st.rerun()

        else:
            st.error("Invalid Username or Password")

# Dashboard
else:

    st.title("Sales Intelligence Hub Dashboard")

    st.success(f"Welcome {st.session_state.username}")

    st.write(f"Role : {st.session_state.role}")
    st.write(f"Branch ID : {st.session_state.branch_id}")

    st.sidebar.title("Menu")

    menu = st.sidebar.selectbox(
        "Select Option",
        [
            "Dashboard",
            "Add Sale",
            "Add Payment",
            "Sales Report",
            "Pending Payments",
            "SQL Queries"
        ]
    )

    # DASHBOARD
    if menu == "Dashboard":
        st.header("Dashboard")
        conn = get_connection()
        cur = conn.cursor()

        if st.session_state.role == "Super Admin":

           cur.execute("""
                SELECT
                    COUNT(*),
                    COALESCE(SUM(gross_sales),0),
                    COALESCE(SUM(received_amount),0),
                    COALESCE(SUM(pending_amount),0)
                 FROM customer_sales
            """)
        else:
            cur.execute("""
                 SELECT
                    COUNT(*),
                    COALESCE(SUM(gross_sales),0),
                    COALESCE(SUM(received_amount),0),
                    COALESCE(SUM(pending_amount),0)
                    FROM customer_sales
                WHERE branch_id = %s
            """, (st.session_state.branch_id,))

        result = cur.fetchone()

        col1, col2, col3, col4 = st.columns(4)

        col1.metric("Total Sales", result[0])
        col2.metric("Gross Sales", f"₹{result[1]}")
        col3.metric("Received Amount", f"₹{result[2]}")
        col4.metric("Pending Amount", f"₹{result[3]}")

        conn.close()

    # ADD SALE
    elif menu == "Add Sale":

        st.header("Add Sale")

        if st.session_state.role == "Super Admin":
            branch_id = st.number_input(
                "Branch ID",
                min_value=1,
                step=1
            )
        else:
            branch_id = st.session_state.branch_id
            st.write(f"Branch ID : {branch_id}")

        sale_date = st.date_input("Sale Date")

        customer_name = st.text_input("Customer Name")

        mobile_number = st.text_input("Mobile Number")

        product_name = st.selectbox(
            "Product Name",
            ["DS", "DA", "BA", "FSD"]
        )

        gross_sales = st.number_input(
            "Gross Sales",
            min_value=0.0
        )

        if st.button("Save Sale"):

            add_sale(
                branch_id,
                sale_date,
                customer_name,
                mobile_number,
                product_name,
                gross_sales
            )

            st.success("Sale Added Successfully")

    # ADD PAYMENT
    elif menu == "Add Payment":
        st.header("Add Payment")
        sale_id = st.number_input(
            "SALE ID",
            min_value=1,
            step=1
        )
        payment_date=st.date_input("Payment Date")
        amount_paid = st.number_input(
            "Amount Paid",
            min_value=0.0
        )
            
        payment_method = st.selectbox(
            "Payment Method",
            ["Cash","UPI","Card"]
        
        )
        if st.button("Save Payment"):
            add_payment(
                sale_id,
                payment_date,
                amount_paid,
                payment_method
            )
            st.success("Payment Added Successfully")
        
        

    # SALES REPORT
    elif menu == "Sales Report":
        st.header("Sales Report")

        conn = get_connection()
        cur = conn.cursor()

        if st.session_state.role == "Super Admin":

             cur.execute("""
                 SELECT sale_id,
                        customer_name,
                        product_name,
                        gross_sales,
                        received_amount,
                        status
                FROM customer_sales
                ORDER BY sale_id
             """)
        else:
            cur.execute("""
                SELECT sale_id,
                        customer_name,
                        product_name,
                        gross_sales,
                        received_amount,
                        status
                FROM customer_sales
                WHERE branch_id = %s
                ORDER BY sale_id
            """, (st.session_state.branch_id,))
        data = cur.fetchall()
        for row in data:
            st.write(row)
        conn.close()
    # PENDING PAYMENTS
    elif menu == "Pending Payments":
        st.header("Pending Payments")
        conn = get_connection()
        cur = conn.cursor()

        if st.session_state.role == "Super Admin":

            cur.execute("""
                SELECT sale_id,
                    customer_name,
                    gross_sales,
                    received_amount,
                    (gross_sales - received_amount) AS pending_amount
                FROM customer_sales
                WHERE status = 'Open'
                ORDER BY sale_id
            """)
        else:
            cur.execute("""
                SELECT sale_id,
                    customer_name,
                    gross_sales,
                    received_amount,
                    (gross_sales - received_amount) AS pending_amount
                FROM customer_sales
                WHERE status = 'Open'
                AND branch_id = %s
                ORDER BY sale_id
            """, (st.session_state.branch_id,))
        data = cur.fetchall()
        for row in data:
            st.write(
                f"Sale ID: {row[0]} | "
                f"Customer: {row[1]} | "
                f"Sales: ₹{row[2]} | "
                f"Received: ₹{row[3]} | "
                f"Pending: ₹{row[4]}"
            )

        conn.close()
    elif menu == "SQL Queries":
         st.header("SQL Queries")
         if st.session_state.role != "Super Admin":
            st.error("Only Super Admin Can Access SQL Queries")
            st.stop()
         conn = get_connection()
         cur = conn.cursor()

         query_option = st.selectbox(
              "Select Query",
             [
                  "Total Gross Sales",
                 "Total Received Amount",
                 "Total Pending Amount",
                 "Open Sales",
                 "Closed Sales",
                 "Top 3 Highest Sales",
                 "Branch Wise Sales Count"
             ]
        )
         if st.button("Run Query"):

            if query_option == "Total Gross Sales":

             cur.execute("""
                    SELECT SUM(gross_sales)
                    FROM customer_sales
                """)
             result= cur.fetchone()

            st.write("Total Gross Sales:",result[0])
         elif query_option == "Total Received Amount":

            cur.execute("""
                SELECT SUM(received_amount)
                FROM customer_sales
            """)
            result= cur.fetchone()

            st.write("Total Received Amount:",result[0] )
         elif query_option == "Total Pending Amount":

            cur.execute("""
                SELECT SUM(pending_amount)
                FROM customer_sales
            """)
            result= cur.fetchone()

            st.write("Total Pending Amount:", result[0])
         elif query_option == "Open Sales":

            cur.execute("""
                SELECT *
                FROM customer_sales
                WHERE status = 'Open'
            """)

            data = cur.fetchall()

            for row in data:
                st.write(row)
         elif query_option == "Closed Sales":
            cur.execute("""
                SELECT sale_id,
                     customer_name,
                     gross_sales,
                     received_amount,
                     status
                FROM customer_sales
                WHERE status = 'Close'
                """)
            data = cur.fetchall()
            for row in data:
                st.write(row)
         elif query_option == "Top 3 Highest Sales":
            cur.execute("""
                SELECT sale_id,
                       customer_name,
                       gross_sales
                FROM customer_sales
                ORDER BY gross_sales DESC
                LIMIT 3
            """)

            data = cur.fetchall()

            for row in data:
                st.write(row)
         elif query_option == "Branch Wise Sales Count":

            cur.execute("""
                SELECT branch_id,
                       COUNT(*)
                FROM customer_sales
                GROUP BY branch_id
            """)

            data = cur.fetchall()

            for row in data:
                st.write(row)
         conn.close()

    # LOGOUT
    if st.sidebar.button("Logout"):
        st.session_state.clear()
        st.rerun()