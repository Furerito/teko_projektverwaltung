import bcrypt
import pyotp
from app.base_utils import get_db_connection

def get_user(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'otp_secret': user[3],
            'two_factor_enabled': user[4],
            'two_factor_verified': user[5],
            'is_superuser': user[6],
            'account_locked': user[7]
        }
    return None

def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE id = %s", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return {
            'id': user[0],
            'username': user[1],
            'password': user[2],
            'otp_secret': user[3],
            'two_factor_enabled': user[4],
            'two_factor_verified': user[5],
            'is_superuser': user[6],
            'account_locked': user[7]
        }
    return None

def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users ORDER BY id ASC")
    users = cur.fetchall()
    cur.close()
    conn.close()
    return users

def create_user(username, password, is_superuser=False):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    otp_secret = pyotp.random_base32()  # Generiere ein zufälliges OTP-Secret
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (username, password, otp_secret, is_superuser) 
            VALUES (%s, %s, %s, %s)
        """, (username, hashed_password.decode('utf-8'), otp_secret, is_superuser))
        conn.commit()
    except Exception as e:
        conn.rollback()  # Rollback bei Fehler
        print(f"Fehler beim Erstellen des Benutzers: {e}")
    finally:
        cur.close()
        conn.close()

def update_user_details(user_id, username, password, account_locked):
    conn = get_db_connection()
    cur = conn.cursor()
    if password:  # Nur hashen und aktualisieren, wenn ein neues Passwort angegeben wurde
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur.execute("""
            UPDATE users 
            SET username = %s, password = %s, account_locked = %s 
            WHERE id = %s
        """, (username, hashed_password.decode('utf-8'), account_locked, user_id))
    else:
        cur.execute("""
            UPDATE users 
            SET username = %s, account_locked = %s 
            WHERE id = %s
        """, (username, account_locked, user_id))
    conn.commit()
    cur.close()
    conn.close()

def delete_user(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = %s", (username,))
    conn.commit()
    cur.close()
    conn.close()

def reset_2fa(user_id):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users 
        SET two_factor_enabled = FALSE, two_factor_verified = FALSE 
        WHERE id = %s
    """, (user_id,))
    conn.commit()
    cur.close()
    conn.close()

def update_user_two_factor_verified(username, verified):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET two_factor_verified = %s WHERE username = %s", (verified, username))
    conn.commit()
    cur.close()
    conn.close()

def enable_user_two_factor(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE users 
        SET two_factor_enabled = TRUE, two_factor_verified = TRUE 
        WHERE username = %s
    """, (username,))
    conn.commit()
    cur.close()
    conn.close()

def update_user_password(username, new_password):
    hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_password.decode('utf-8'), username))
    conn.commit()
    cur.close()
    conn.close()
