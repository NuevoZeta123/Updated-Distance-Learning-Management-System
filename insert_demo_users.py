import mysql.connector
from werkzeug.security import generate_password_hash

# MySQL Configuration
MYSQL_CONFIG = {
    'host': 'switchback.proxy.rlwy.net',
    'user': 'root',
    'password': 'AiwBbAmtKMRHmCRijzEFhNTtmyJYWwmW',
    'database': 'dlms',
    'port': 51540
}

def insert_demo_users():
    try:
        conn = mysql.connector.connect(**MYSQL_CONFIG)
        cur = conn.cursor()

        # Demo users data
        users = [
            ('Administrator', 'admin@dlms.com', 'admin123', 'administrator'),
            ('John Doe Lecturer', 'lecturer@dlms.com', 'lecturer123', 'lecturer'),
            ('Jane Doe Student', 'student@dlms.com', 'student123', 'student')
        ]

        for full_name, email, password, role in users:
            password_hash = generate_password_hash(password)
            cur.execute("""
                INSERT INTO users (full_name, email, password_hash, role, is_active)
                VALUES (%s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                full_name = VALUES(full_name),
                password_hash = VALUES(password_hash),
                role = VALUES(role),
                is_active = VALUES(is_active)
            """, (full_name, email, password_hash, role, True))

        conn.commit()
        print("Demo users inserted successfully!")

    except mysql.connector.Error as err:
        print(f"Database error: {err}")
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    insert_demo_users()