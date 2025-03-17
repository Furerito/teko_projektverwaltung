from app import db

# Datenbankmodell
class Person(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    vorname = db.Column(db.String(100), nullable=False)
    nachname = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), nullable=False)
    telefonnummer = db.Column(db.String(20), nullable=False)
    strasse = db.Column(db.String(255), nullable=False)
    hausnummer = db.Column(db.String(10), nullable=False)
    postleitzahl = db.Column(db.String(10), nullable=False)
    stadt = db.Column(db.String(100), nullable=False)