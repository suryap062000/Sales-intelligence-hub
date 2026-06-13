from db import get_connection

def add_sale(branch_id, sale_date, customer_name,
             mobile_number, product_name, gross_sales):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO customer_sales
        (branch_id, sale_date, customer_name,
         mobile_number, product_name, gross_sales,
         received_amount, status)
        VALUES (%s,%s,%s,%s,%s,%s,0,'Open')
    """,
    (branch_id, sale_date, customer_name,
     mobile_number, product_name, gross_sales))

    conn.commit()
    print("Sale inserted successfully")
    conn.close()