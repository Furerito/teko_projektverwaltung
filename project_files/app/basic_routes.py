from flask import render_template, request, redirect, url_for, session, current_app, flash as flask_flash
from app.auth import login_required, superuser_required
from app.base_utils import *
import pyotp
import qrcode
import io
from base64 import b64encode
import bcrypt  # Das benötigte Modul wird hier importiert
from flask import flash
from app.users import update_user_password
import urllib.parse
import os
from configparser import ConfigParser
from app.config import *
import subprocess


print('routes.py')

# Config laden
config = ConfigParser()
config.read('config.ini')

# Upload-Parameter aus der config.ini
UPLOAD_FOLDER = config['uploads']['upload_folder']
ALLOWED_EXTENSIONS = set(config['uploads']['allowed_extensions'].split(','))

# Sicherstellen, dass der UPLOAD_FOLDER existiert
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Überprüfen, ob Dateiendung erlaubt ist
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def flash(message, category="info"):
    flask_flash(message, category)


def init_basic_routes(app, db):

    # Routen für Datenbankoperationen
    @app.route('/db/init', methods=['GET'])
    def init_db():
        db.create_all()
        return jsonify({'message': 'Datenbank wurde initialisiert'})

    @app.route('/db/migrate', methods=['GET'])
    def migrate_db():
        try:
            subprocess.run(['flask', 'db', 'migrate', '-m', 'Automatische Migration'], check=True)
            subprocess.run(['flask', 'db', 'upgrade'], check=True)
            return jsonify({'message': 'Migration erfolgreich durchgeführt'})
        except subprocess.CalledProcessError as e:
            return jsonify({'error': str(e)})

    @app.route('/db/reset', methods=['GET'])
    def reset_db():
        db.drop_all()
        db.create_all()
        return jsonify({'message': 'Datenbank wurde zurückgesetzt'})
    
    @app.route('/', endpoint='home', methods=['GET', 'POST'])
    def home():
        app_logo = config['app']['logo']
        return render_template('base/login.html', app_logo=app_logo)

    @app.route('/login', methods=['POST'])
    def login():
        username = request.form['username']
        password = request.form['password']

        user = get_user(username)
        if user and not user['account_locked'] and bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            session['username'] = username
            session['user'] = user
            print(session)
            session.permanent = True  # Markiert die Session als permanent, um das Timeout zu aktivieren
            update_user_two_factor_verified(username, False)
            return redirect(url_for('two_factor'))
        
        flash("Login fehlgeschlagen oder Account gesperrt.", "warning")

        return redirect(url_for('home'))

    @app.route('/2fa')
    def two_factor():
        if 'user' not in session:
            return redirect(url_for('home'))

        username = session['username']
        user = get_user(username)

        if user['two_factor_verified']:
            return redirect(url_for('dashboard'))

        if user['two_factor_enabled']:
            return render_template('base/verify_otp.html')
        else:
            otp_secret = user['otp_secret']
            issuer_name = config['flask']['issuer_name']
            image_url = config['app']['logo']  # Der Pfad zum Logo in der Konfigurationsdatei
            
            # URL encode the TOTP URI
            encoded_image_uri = urllib.parse.quote("android-chrome-192x192.png", safe='')
            
            # Manuelle Erstellung der TOTP-URI mit dem image-Parameter
            totp_uri = f"otpauth://totp/{issuer_name}:{username}?secret={otp_secret}&issuer={issuer_name}&image="+encoded_image_uri
            
            
            # Generiere den QR-Code mit der angepassten URI
            qr = qrcode.make(totp_uri)
            buffer = io.BytesIO()
            qr.save(buffer, format="PNG")
            qr_data = b64encode(buffer.getvalue()).decode('utf-8')

            return render_template('base/2fa.html', qr_data=qr_data, logo_path=image_url)

    @app.route('/verify', methods=['POST'])
    def verify():
        otp = request.form['otp']
        username = session.get('username')

        if username:
            user = get_user(username)
            otp_secret = user['otp_secret']
            totp = pyotp.TOTP(otp_secret)
            if totp.verify(otp):
                enable_user_two_factor(username)
                return redirect(url_for('dashboard'))

        return redirect(url_for('two_factor'))

    @app.route('/dashboard')
    @login_required
    def dashboard():
        
        user = get_user(session['username'])
        return render_template('base/dashboard.html', is_superuser=user['is_superuser'], user=user)

    

    @app.route('/manage_users', methods=['GET', 'POST'])
    @login_required
    @superuser_required
    def manage_users():
        user = get_user(session['username'])
        if request.method == 'POST':
            if 'add_user' in request.form:
                # Neuen Benutzer hinzufügen
                new_username = request.form['new_username']
                new_password = request.form['new_password']
                new_is_superuser = 'new_is_superuser' in request.form

                if get_user(new_username):
                    return 'Benutzername existiert bereits!', 400
                
                create_user(new_username, new_password, new_is_superuser)
                flash(f"Benutzer <strong>{new_username}</strong> erfolgreich angelegt.", "success")
                return redirect(url_for('manage_users'))

            elif 'edit_user' in request.form:
                # Bestehenden Benutzer bearbeiten
                user_id = request.form['user_id']
                username = request.form['username']
                password = request.form['password']
                is_superuser = 'is_superuser' in request.form
                account_locked = 'account_locked' in request.form
                update_user_details(user_id, username, password, is_superuser, account_locked)
                flash(f"Benutzer <strong>{username}</strong> erfolgreich bearbeitet.", "success")
                return redirect(url_for('manage_users'))
            
                

            elif 'reset_2fa' in request.form:
                # 2FA für einen Benutzer zurücksetzen
                user_id = request.form['user_id']
                reset_2fa(user_id)
                flash(f"Benutzer <strong>{username}</strong> MFA zurückgesetzt.", "success")
                return redirect(url_for('base/manage_users'))

            elif 'delete_user' in request.form:
                # Benutzer löschen
                user_id = request.form['user_id']
                user = get_user_by_id(user_id)
                if user:
                    delete_user(user['username'])

                flash(f"Benutzer <strong>{user_id}</strong> gelöscht.", "success")
                return redirect(url_for('manage_users'))
        
        users = get_all_users()
        return render_template('base/manage_users.html', users=users, is_superuser=user['is_superuser'])
        
    @app.route('/change_password', methods=['GET', 'POST'])
    @login_required
    def change_password():
        if request.method == 'POST':
            current_password = request.form['current_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
    
            user = get_user(session['username'])
    
            # Überprüfen, ob das aktuelle Passwort korrekt ist
            if not bcrypt.checkpw(current_password.encode('utf-8'), user['password'].encode('utf-8')):
                flash('Das aktuelle Passwort ist falsch.', 'error')
                return redirect(url_for('change_password'))
    
            # Überprüfen, ob das neue Passwort und die Bestätigung übereinstimmen
            if new_password != confirm_password:
                flash('Das neue Passwort und die Bestätigung stimmen nicht überein.', 'error')
                return redirect(url_for('change_password'))
    
            # Passwort aktualisieren
            update_user_password(user['username'], new_password)
    
            flash('Dein Passwort wurde erfolgreich geändert.', 'success')
            return redirect(url_for('dashboard'))
            
        user = get_user(session['username'])
        return render_template('base/change_password.html', is_superuser=user['is_superuser'])
    
    

    @app.route('/konfiguration', methods=['GET', 'POST'])
    @login_required
    def konfiguration():
        if request.method == 'POST':
            # Speichere die Konfigurationsdaten in der Konfigurationsdatei
            config['mail']['server'] = request.form['smtp_server']
            config['mail']['port'] = request.form['smtp_port']
            config['mail']['user'] = request.form['smtp_user']
            config['mail']['password'] = request.form['smtp_password']
            config['mail']['from'] = request.form['smtp_from']
            config['mail']['report_recipient'] = request.form['report_recipient']
            config['mail']['report_cc'] = request.form['report_cc']
            config['mail']['report_subject'] = request.form['report_subject']
            
            with open('config.ini', 'w') as configfile:
                config.write(configfile)
            flash('Konfiguration erfolgreich gespeichert.', 'success')
            return redirect(url_for('base/konfiguration'))
        
        user = get_user(session['username'])
        return render_template('base/konfiguration.html', config=config, is_superuser=user['is_superuser'])


    @app.route('/logout', methods=['GET', 'POST'])
    def logout():
        session.clear()
        return redirect(url_for('home'))