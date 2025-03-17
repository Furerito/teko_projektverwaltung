import psycopg2
import psycopg2.extras
import bcrypt
import pyotp
from flask import current_app, flash, jsonify
import json
import psycopg2
from psycopg2 import sql
from datetime import datetime
from json import loads  # JSON laden, um es in Python-Daten zu konvertieren
from configparser import ConfigParser

# Config laden
config = ConfigParser()
config.read('config.ini')

def get_db_connection():
    conn = psycopg2.connect(
        host=config['database']['host'],
        database=config['database']['database'],
        user=config['database']['user'],
        password=config['database']['password'],
        port=config['database']['port'] 
    )
    return conn

def get_user(username):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE username = %s LIMIT 1", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return user
      
    return None

def get_all_users():
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)  # Verwende DictCursor
    cur.execute("SELECT * FROM users ORDER BY id ASC")
    users = cur.fetchall()  # Jeder Eintrag ist jetzt ein Dictionary
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

def update_user_details(user_id, username, password, is_superuser, account_locked):
    conn = get_db_connection()
    cur = conn.cursor()
    if password:  # Nur hashen und aktualisieren, wenn ein neues Passwort angegeben wurde
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        cur.execute("""
            UPDATE users 
            SET username = %s, password = %s, is_superuser=%s, account_locked = %s 
            WHERE id = %s
        """, (username, hashed_password.decode('utf-8'), is_superuser, account_locked, user_id))
    else:
        cur.execute("""
            UPDATE users 
            SET username = %s, is_superuser=%s, account_locked = %s 
            WHERE id = %s
        """, (username, is_superuser, account_locked, user_id))
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

def delete_user(username):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username = %s", (username,))
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

def get_user_by_id(user_id):
    conn = get_db_connection()
    cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    cur.execute("SELECT * FROM users WHERE id = %s LIMIT 1", (user_id,))
    user = cur.fetchone()
    cur.close()
    conn.close()
    if user:
        return user
      
    return None


# Daten aus Formular einlesen
# Einzelner Eintrag manuell anlegen
def insert_single_row_in_kurse(form):
    conn = get_db_connection()
    cur = conn.cursor()

    name = form.get('name')
    vorname = form.get('vorname')
    geburtsdatum = form.get('geburtsdatum')
    email = form.get('email')
    eib_name = form.get('eib_name')
    eib_adresse = form.get('eib_adresse')
    ph = form.get('ph')
    kursdurchfuehrung = form.get('kursdurchfuehrung')
    kursnummer = form.get('kursnummer')
    kommentar = form.get('kommentar')

    cur.execute("""
        INSERT INTO kurse (name, vorname, geburtsdatum, email, eib_name, eib_adresse, ph, kursdurchfuehrung, kursnummer, kommentar) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (name, vorname, geburtsdatum, email, eib_name, eib_adresse, ph, kursdurchfuehrung, kursnummer, kommentar))
    conn.commit()
    flash('Eintrag erfolgreich hinzugefügt.', 'success')


def delete_single_row_in_kurse(kursnummer, email):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("DELETE FROM kurse WHERE kursnummer = %s AND email = %s", (kursnummer, email))
    conn.commit()

    cur.execute("DELETE FROM praesenz_links WHERE kursnummer = %s AND email = %s", (kursnummer, email))
    conn.commit()

    cur.close()
    conn.close()


def delete_kurs_in_kurse(kursnummer):
    conn = get_db_connection()
    cur = conn.cursor()
    
    cur.execute("DELETE FROM kurse WHERE kursnummer = %s", (kursnummer,))
    conn.commit()

    cur.execute("DELETE FROM praesenz_links WHERE kursnummer = %s", (kursnummer,))
    conn.commit()

    cur.close()
    conn.close()


# Daten aus json File einlesen
def insert_kursdata_if_not_exists(json_file):
    """
    Liest JSON-Daten und fügt sie in die PostgreSQL-Tabelle ein, wenn kursnummer und email nicht existieren.
    """
    # JSON-Daten laden
    with open(json_file, "r", encoding="utf-8") as file:
        data = json.load(file)

    # Extrahiere die strukturierten Tabellen-Daten
    entries = data["structured_table"]

    # Verbindung zur PostgreSQL-Datenbank
    conn = get_db_connection()
    cursor = conn.cursor()

    for entry in entries:
        kursnummer = entry["Kursnummer"]
        email = entry["E-Mail"]

        # Prüfen, ob der Eintrag bereits existiert
        cursor.execute(
            "SELECT 1 FROM kurse WHERE kursnummer = %s AND email = %s",
            (kursnummer, email)
        )
        if not cursor.fetchone():  # Wenn nichts gefunden wird
            # Daten einfügen
            insert_query = """
                INSERT INTO kurse (name, vorname, geburtsdatum, email, eib_name, 
                                   eib_adresse, ph, kursdurchfuehrung, kursnummer, kommentar)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            cursor.execute(insert_query, (
                entry["Name"],
                entry["Vorname"],
                entry["Geburtsdatum"],
                entry["E-Mail"],
                entry["EiB-Name"],
                entry["EiB-Adresse"],
                entry["PH"],
                entry["Kursdurchführung"],
                entry["Kursnummer"],
                entry["Kommentar"]
            ))
            #flash(f"Eintrag hinzugefügt: {entry['Name']} {entry['Vorname']} - {email}")
        else:
            flash(f"Eintrag übersprungen (bereits vorhanden): {entry['Name']} {entry['Vorname']} - {email}", "warning")

    # Änderungen speichern und Verbindung schliessen
    conn.commit()
    cursor.close()
    conn.close()
    flash("Daten in Datenbank aufgenommen", "success")

    return True


def get_kurse_json():
    try:
        # Verbindung zur PostgreSQL-Datenbank
        conn = get_db_connection()
        cursor = conn.cursor()

        # SQL-Abfrage: Geburtsdatum direkt formatieren
        cursor.execute("""
            SELECT 
                id,
                name, 
                vorname, 
                geburtsdatum, 
                email, 
                eib_name, 
                eib_adresse, 
                ph, 
                kursdurchfuehrung, 
                kursnummer, 
                kommentar
            FROM kurse
        """)
        rows = cursor.fetchall()

        # Spaltennamen aus der Datenbank-Abfrage (in der richtigen Reihenfolge)
        colnames = [desc[0] for desc in cursor.description]

        # Daten in JSON-Format umwandeln
        data = [dict(zip(colnames, row)) for row in rows]

        # Verbindung schliessen
        cursor.close()
        conn.close()

        # JSON mit Spaltennamen und Daten zurückgeben
        return jsonify({"columns": colnames, "data": data})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

def get_distinct_kursnummern():
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT DISTINCT kursnummer FROM kurse")
    kurse = cur.fetchall()
    cur.close()
    conn.close()
    return kurse


def get_entries_for_kursnummer(kursnummer):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT k.id, k.name, k.vorname, k.email, k.kursnummer, pl.anwesend
        FROM kurse k
        LEFT JOIN praesenz_links pl ON k.email = pl.email AND k.kursnummer = pl.kursnummer
        WHERE k.kursnummer = %s 
    """, (kursnummer,))
    data = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return data, colnames


def get_report_for_kursnummer(kursnummer):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT 
            k.*,
            CASE 
                WHEN pl.anwesend = TRUE THEN 'Ja'
                ELSE 'Nein'
            END AS anwesend_status
        FROM kurse k
        LEFT JOIN praesenz_links pl 
            ON k.email = pl.email AND k.kursnummer = pl.kursnummer
        WHERE k.kursnummer = %s;

    """, (kursnummer,))
    data = cur.fetchall()
    colnames = [desc[0] for desc in cur.description]
    cur.close()
    conn.close()
    return data, colnames



