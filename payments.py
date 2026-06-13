from db import get_connection

def add_payment(sale_id, payment_date, amount_paid, payment_method):

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO payment_splits
        (sale_id, payment_date, amount_paid, payment_method)
        VALUES (%s,%s,%s,%s)
    """,
    (sale_id, payment_date, amount_paid, payment_method))

    conn.commit()
    conn.close()