from flask import jsonify, render_template, request
from app import db
from app.models.kontakte_model import Person
from app.schemas.kontakte_schema import PersonSchema
from app.auth import *


def init_kontakte_routes(app):
   
    person_schema = PersonSchema()
    personen_schema = PersonSchema(many=True)

    @app.route('/kontakte', methods=['GET', 'POST'])
    @login_required
    def kontakte():
        user = get_user(session['username'])
        return render_template('base/kontakte.html', is_superuser=user['is_superuser'])

    #  Routen für Personen
    @app.route('/personen', methods=['POST'])
    def erstelle_person():
        vorname = request.json['vorname']
        nachname = request.json['nachname']
        email = request.json['email']
        telefonnummer = request.json['telefonnummer']
        strasse = request.json['strasse']
        hausnummer = request.json['hausnummer']
        postleitzahl = request.json['postleitzahl']
        stadt = request.json['stadt']

        neue_person = Person(vorname=vorname, nachname=nachname, email=email, telefonnummer=telefonnummer,
                            strasse=strasse, hausnummer=hausnummer, postleitzahl=postleitzahl, stadt=stadt)
        db.session.add(neue_person)
        db.session.commit()

        return person_schema.jsonify(neue_person)

    @app.route('/personen', methods=['GET'])
    def alle_personen():
        personen = Person.query.all()
        return personen_schema.jsonify(personen)

    @app.route('/personen/<int:id>', methods=['GET'])
    def einzelne_person(id):
        person = Person.query.get(id)
        return person_schema.jsonify(person)

    @app.route('/personen/<int:id>', methods=['PUT'])
    def update_person(id):
        person = Person.query.get(id)
        if not person:
            return jsonify({'error': 'Person nicht gefunden'}), 404

        person.vorname = request.json.get('vorname', person.vorname)
        person.nachname = request.json.get('nachname', person.nachname)
        person.email = request.json.get('email', person.email)
        person.telefonnummer = request.json.get('telefonnummer', person.telefonnummer)
        person.strasse = request.json.get('strasse', person.strasse)
        person.hausnummer = request.json.get('hausnummer', person.hausnummer)
        person.postleitzahl = request.json.get('postleitzahl', person.postleitzahl)
        person.stadt = request.json.get('stadt', person.stadt)

        db.session.flush()  # Änderungen in die DB schreiben, aber nicht committen
        db.session.commit()  # Endgültig speichern

        db.session.refresh(person)  # Stelle sicher, dass die neueste Version geladen wird

        return person_schema.jsonify(person)


    @app.route('/personen/<int:id>', methods=['DELETE'])
    def delete_person(id):
        person = Person.query.get(id)
        db.session.delete(person)
        db.session.commit()
        return jsonify({'message': 'Person gelöscht'})

    # Return the Person model so it can be used in other routes
    return Person

