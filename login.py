from db import get_connection

def login(username, password):
    conn = get_connection()

    cur = conn.cursor()

    cur.execute(
        "select * from users where username=%s and password=%s",
        (username, password)
    )

    user = cur.fetchone()

    conn.close()

    return user