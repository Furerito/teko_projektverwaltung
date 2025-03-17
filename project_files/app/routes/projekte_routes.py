from flask import jsonify, request, render_template, session
from app import db
from werkzeug.utils import secure_filename  
from datetime import datetime               
from app.models.projekte_model import *
from app.models.kontakte_model import Person
from app.schemas.projekte_schema import *
from app.auth import login_required
from app.base_utils import get_user
import os
from configparser import ConfigParser
from app.schemas.projekte_schema import AktivitaetSchema
from datetime import datetime  # Import für datetime.datetime
    

# config.ini laden
base_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(base_dir, '../../config.ini')
config = ConfigParser()
config.read(config_path)

UPLOAD_FOLDER = config['uploads']['upload_folder']


def init_projekte_routes(app):

    projekt_schema = ProjektSchema()
    projekte_schema = ProjektSchema(many=True)

    projektphase_schema = ProjektphaseSchema()
    projektphasee_schema = ProjektphaseSchema(many=True)

    dokument_schema = DokumentSchema()
    dokumente_schema = DokumentSchema(many=True)
    
    aktivitaet_schema = AktivitaetSchema()
    aktivitaeten_schema = AktivitaetSchema(many=True)
    
    # API-Endpunkte für Projekte
    @app.route('/projekte', methods=['POST'])
    def erstelle_projekt():
        data = request.json
        data['prioritaet'] = PrioritaetEnum(data['prioritaet'])
        data['status'] = ProjektStatusEnum(data['status'])
        data['vorgehensmodell'] = VorgehensmodellEnum(data['vorgehensmodell'])
        neues_projekt = Projekt(**data)
        db.session.add(neues_projekt)
        db.session.commit()
        return projekt_schema.jsonify(neues_projekt)

    @app.route('/projekte', methods=['GET'])
    def alle_projekte():
        result = db.session.query(Projekt, Person).join(
            Person, Projekt.projektleiter_id == Person.id
        ).all()

        response_data = []
        for projekt, person in result:
            projekt_data = projekt_schema.dump(projekt)
            projekt_data['prioritaet'] = projekt.prioritaet.value
            projekt_data['status'] = projekt.status.value
            projekt_data['vorgehensmodell'] = projekt.vorgehensmodell.value
            projekt_data['projektleiter_name'] = f"{person.vorname} {person.nachname}"
            response_data.append(projekt_data)

        return jsonify(response_data)


    @app.route('/projekte/<int:id>', methods=['GET'])
    def einzelnes_projekt(id):
        projekt = Projekt.query.get(id)
        projekt_data = projekt_schema.dump(projekt)

        projekt_data['prioritaet'] = projekt.prioritaet.value
        projekt_data['status'] = projekt.status.value
        projekt_data['vorgehensmodell'] = projekt.vorgehensmodell.value

        return jsonify(projekt_data)

    @app.route('/projekte/<int:id>', methods=['PUT'])
    def update_projekt(id):
        projekt = Projekt.query.get(id)
        data = request.json

        data['prioritaet'] = PrioritaetEnum(data['prioritaet'])
        data['status'] = ProjektStatusEnum(data['status'])
        data['vorgehensmodell'] = VorgehensmodellEnum(data['vorgehensmodell'])

        for key, value in data.items():
            setattr(projekt, key, value)

        db.session.commit()
        return projekt_schema.jsonify(projekt)

    @app.route('/projekte/<int:id>', methods=['DELETE'])
    def delete_projekt(id):
        projekt = Projekt.query.get(id)
        db.session.delete(projekt)
        db.session.commit()
        return jsonify({'message': 'Projekt gelöscht'})

    @app.route('/projekte/<int:projekt_id>/phasen', methods=['GET'])
    def get_phasen(projekt_id):
        phasen = Projektphase.query.filter_by(projekt_id=projekt_id).all()
        return projektphasee_schema.jsonify(phasen)

    @app.route('/projektphasen', methods=['POST'])
    def erstelle_projektphase():
        data = request.json
        phase = Projektphase(**data)
        db.session.add(phase)
        db.session.commit()
        return projektphase_schema.jsonify(phase)

    @app.route('/projektphasen/<int:id>', methods=['PUT'])
    def bearbeite_projektphase(id):
        phase = Projektphase.query.get(id)
        data = request.json
        for key, value in data.items():
            setattr(phase, key, value)
        db.session.commit()
        return projektphase_schema.jsonify(phase)
    
    @app.route('/projektphasen/<int:id>', methods=['GET'])
    def get_einzelne_phase(id):
        """
        Liefert eine einzelne Projektphase anhand der ID zurück.
        Gibt einen HTTP-Status 404 zurück, falls die Phase nicht existiert.
        """
        phase = Projektphase.query.get(id)
        if not phase:
            return jsonify({"error": "Projektphase nicht gefunden"}), 404

        return projektphase_schema.jsonify(phase)
    
    @app.route('/projektphasen/<int:id>', methods=['DELETE'])
    def delete_projektphase(id):
        phase = Projektphase.query.get(id)
        db.session.delete(phase)
        db.session.commit()
        return jsonify({'message': 'Projektphase gelöscht'})

    # API-Endpunkte für Meilensteine
    @app.route('/projekte/<int:projekt_id>/meilensteine', methods=['GET'])
    def get_meilensteine(projekt_id):
        """
        Liefert alle Meilensteine eines Projekts zurück, inklusive Informationen zur Projektphase.
        """
        meilensteine = Meilenstein.query.filter_by(projekt_id=projekt_id).all()
        
        result = []
        for meilenstein in meilensteine:
            meilenstein_data = MeilensteinSchema().dump(meilenstein)
            
            # Füge Informationen zur Projektphase hinzu, falls vorhanden
            if meilenstein.projektphase_id:
                phase = Projektphase.query.get(meilenstein.projektphase_id)
                if phase:
                    meilenstein_data['phase_id'] = phase.id
                    meilenstein_data['phase_name'] = phase.phase_name
            
            result.append(meilenstein_data)
            
        return jsonify(result)

    @app.route('/meilensteine', methods=['POST'])
    def erstelle_meilenstein():
        """
        Erstellt einen neuen Meilenstein.
        """
        data = request.json
        neuer_meilenstein = Meilenstein(**data)
        db.session.add(neuer_meilenstein)
        db.session.commit()
        meilenstein_schema = MeilensteinSchema()
        return meilenstein_schema.jsonify(neuer_meilenstein), 201

    @app.route('/meilensteine/<int:id>', methods=['GET'])
    def get_einzelner_meilenstein(id):
        """
        Liefert einen einzelnen Meilenstein anhand der ID zurück.
        Gibt einen HTTP-Status 404 zurück, falls der Meilenstein nicht existiert.
        """
        meilenstein = Meilenstein.query.get(id)
        if not meilenstein:
            return jsonify({"error": "Meilenstein nicht gefunden"}), 404
        
        meilenstein_schema = MeilensteinSchema()
        meilenstein_data = meilenstein_schema.dump(meilenstein)
        
        # Füge projekt_id und phase_id hinzu
        meilenstein_data['projekt_id'] = meilenstein.projekt_id
        if hasattr(meilenstein, 'projektphase_id'):
            meilenstein_data['phase_id'] = meilenstein.projektphase_id
            
        return jsonify(meilenstein_data)

    @app.route('/meilensteine/<int:id>', methods=['PUT'])
    def bearbeite_meilenstein(id):
        """
        Aktualisiert einen Meilenstein anhand der ID.
        """
        meilenstein = Meilenstein.query.get(id)
        if not meilenstein:
            return jsonify({"error": "Meilenstein nicht gefunden"}), 404
        
        data = request.json
        # Handle empty projektphase_id
        if 'projektphase_id' in data and (data['projektphase_id'] == '' or data['projektphase_id'] is None):
            data['projektphase_id'] = None
            
        for key, value in data.items():
            setattr(meilenstein, key, value)
        
        db.session.commit()
        meilenstein_schema = MeilensteinSchema()
        return meilenstein_schema.jsonify(meilenstein)

    @app.route('/meilensteine/<int:id>', methods=['DELETE'])
    def delete_meilenstein(id):
        meilenstein = Meilenstein.query.get(id)
        db.session.delete(meilenstein)
        db.session.commit()
        return jsonify({'message': 'Meilenstein gelöscht'})


    @app.route('/aktivitaeten/<int:id>', methods=['DELETE'])
    def delete_aktivitaet(id):
        aktivitaet = Aktivitaet.query.get(id)
        db.session.delete(aktivitaet)
        db.session.commit()
        return jsonify({'message': 'Aktivität gelöscht'})


    # API-Endpunkte für Externe Kosten
    @app.route('/kosten', methods=['POST'])
    def erstelle_kosten():
        data = request.json
        neue_kosten = ExterneKosten(**data)
        db.session.add(neue_kosten)
        db.session.commit()
        return externekosten_schema.jsonify(neue_kosten)

    @app.route('/kosten/<int:id>', methods=['DELETE'])
    def delete_kosten(id):
        kosten = ExterneKosten.query.get(id)
        db.session.delete(kosten)
        db.session.commit()
        return jsonify({'message': 'Kosten gelöscht'})

    # API-Endpunkte für Rapporte
    @app.route('/rapporte', methods=['POST'])
    def erstelle_rapport():
        data = request.json
        neuer_rapport = Rapport(**data)
        db.session.add(neuer_rapport)
        db.session.commit()
        return rapport_schema.jsonify(neuer_rapport)

    @app.route('/rapporte/<int:id>', methods=['DELETE'])
    def delete_rapport(id):
        rapport = Rapport.query.get(id)
        db.session.delete(rapport)
        db.session.commit()
        return jsonify({'message': 'Rapport gelöscht'})
    
    @app.route('/projekte/<int:projekt_id>/aktivitaeten', methods=['GET'])
    def get_aktivitaeten(projekt_id):
        # Query aktivitaeten through the projektphase relationship
        aktivitaeten = db.session.query(Aktivitaet).join(
            Projektphase, Aktivitaet.projektphase_id == Projektphase.id
        ).filter(
            Projektphase.projekt_id == projekt_id
        ).all()
        
        result = []
        for aktivitaet in aktivitaeten:
            aktivitaet_data = aktivitaet_schema.dump(aktivitaet)
            # Get phase information
            phase = Projektphase.query.get(aktivitaet.projektphase_id)
            if phase:
                aktivitaet_data['phase_name'] = phase.phase_name
            
            # Get resource information if available
            if aktivitaet.ressourcen:
                ressource = Person.query.get(aktivitaet.ressourcen)
                if ressource:
                    aktivitaet_data['ressource_name'] = f"{ressource.vorname} {ressource.nachname}"
            
            result.append(aktivitaet_data)
        
        return jsonify(result)

    
    @app.route('/aktivitaeten', methods=['POST'])
    def erstelle_aktivitaet_in_phase():
        data = request.json
        neue_aktivitaet = Aktivitaet(**data)
        db.session.add(neue_aktivitaet)
        db.session.commit()
        
        return aktivitaet_schema.jsonify(neue_aktivitaet), 201

    @app.route('/aktivitaeten/<int:id>', methods=['GET'])
    def get_einzelne_aktivitaet(id):
        """
        Liefert eine einzelne Aktivität anhand der ID zurück.
        Gibt einen HTTP-Status 404 zurück, falls die Aktivität nicht existiert.
        """
        aktivitaet = Aktivitaet.query.get(id)
        if not aktivitaet:
            return jsonify({"error": "Aktivität nicht gefunden"}), 404

        aktivitaet_data = aktivitaet_schema.dump(aktivitaet)
        
        # Get phase information
        phase = Projektphase.query.get(aktivitaet.projektphase_id)
        if phase:
            aktivitaet_data['phase_name'] = phase.phase_name
            aktivitaet_data['phase_id'] = phase.id
        
        # Get resource information if available
        if aktivitaet.ressourcen:
            ressource = Person.query.get(aktivitaet.ressourcen)
            if ressource:
                aktivitaet_data['ressource_name'] = f"{ressource.vorname} {ressource.nachname}"
                aktivitaet_data['ressource_id'] = ressource.id
                
        return jsonify(aktivitaet_data)
    
    @app.route('/aktivitaeten/<int:id>', methods=['PUT'])
    def bearbeite_aktivitaet(id):
        aktivitaet = Aktivitaet.query.get(id)
        data = request.json
        for key, value in data.items():
            setattr(aktivitaet, key, value)
        db.session.commit()
        return aktivitaet_schema.jsonify(aktivitaet)

    @app.route('/projektverwaltung', methods=['GET'])
    @login_required
    def projektverwaltung():
        user = get_user(session['username'])
        return render_template('specific/projekte.html', is_superuser=user['is_superuser'])


    @app.route('/phasenverwaltung/<int:projekt_id>', methods=['GET'])
    @login_required
    def phasenverwaltung(projekt_id):
        user = get_user(session['username'])
        return render_template('specific/phasen.html', is_superuser=user['is_superuser'], projekt_id=projekt_id)


    @app.route('/projekte/<int:projekt_id>/dokumente', methods=['GET'])
    def get_dokumente(projekt_id):
        dokumente = Dokument.query.filter_by(projekt_id=projekt_id).all()
        result = []
        for dok in dokumente:
            item = dokument_schema.dump(dok)
            item['url'] = f"/{dok.dateipfad}"
            result.append(item)
        return jsonify(result)

    @app.route('/projekte/<int:projekt_id>/dokumente', methods=['POST'])
    def upload_dokument(projekt_id):
        file = request.files.get('file')
        if file:
            filename = secure_filename(file.filename)
            dateipfad = os.path.join(UPLOAD_FOLDER, filename)
            file.save(dateipfad)

            dokument = Dokument(
                dokumentenname=filename,
                dateipfad=dateipfad,
                typ=file.content_type,
                hochladedatum=datetime.utcnow(),
                projekt_id=projekt_id
            )
            db.session.add(dokument)
            db.session.commit()

            return dokument_schema.jsonify(dokument), 201
        return jsonify({'error': 'Keine Datei ausgewählt'}), 400

    @app.route('/dokumente/<int:id>', methods=['DELETE'])
    def delete_dokument(id):
        dokument = Dokument.query.get(id)
        if dokument:
            try:
                os.remove(dokument.dateipfad)
            except Exception as e:
                print(e)
            db.session.delete(dokument)
            db.session.commit()
            return jsonify({'message': 'Dokument gelöscht'})
        return jsonify({'error': 'Dokument nicht gefunden'}), 404


    @app.route('/projekte/<int:projekt_id>/gantt', methods=['GET'])
    def get_projekt_gantt(projekt_id):
        # Projektdaten abfragen
        projekt = Projekt.query.get(projekt_id)
        if not projekt:
            return jsonify({"error": "Projekt nicht gefunden"}), 404

        # Projektphasen abfragen
        phasen = Projektphase.query.filter_by(projekt_id=projekt_id).all()

        # Tasks für das Gantt-Chart erstellen
        tasks = []
        for phase in phasen:
            # Phase als Task hinzufügen
            phase_start = datetime.combine(phase.startdatum_geplant, datetime.min.time())  # Umwandlung in datetime.datetime
            phase_end = datetime.combine(phase.enddatum_geplant, datetime.min.time())  # Umwandlung in datetime.datetime

            phase_task = {
                "id": f"phase_{phase.id}",
                "name": phase.phase_name,
                "start": phase_start.isoformat(),
                "end": phase_end.isoformat(),
                "progress": phase.fortschritt or 0,
                "dependencies": "",  # Keine Abhängigkeiten für Phasen
                "custom_class": "phase-task"  # Optional: CSS-Klasse für Phasen
            }
            tasks.append(phase_task)

            # Aktivitäten der Phase als Unter-Tasks hinzufügen
            aktivitaeten = Aktivitaet.query.filter_by(projektphase_id=phase.id).all()
            for aktivitaet in aktivitaeten:
                aktivitaet_start = datetime.combine(aktivitaet.startdatum_geplant, datetime.min.time())  # Umwandlung in datetime.datetime
                aktivitaet_end = datetime.combine(aktivitaet.enddatum_geplant, datetime.min.time())  # Umwandlung in datetime.datetime

                aktivitaet_task = {
                    "id": f"aktivitaet_{aktivitaet.id}",
                    "name": aktivitaet.name,
                    "start": aktivitaet_start.isoformat(),
                    "end": aktivitaet_end.isoformat(),
                    "progress": aktivitaet.fortschritt or 0,
                    "dependencies": f"phase_{phase.id}",  # Abhängigkeit von der übergeordneten Phase
                    "custom_class": "aktivitaet-task"  # Optional: CSS-Klasse für Aktivitäten
                }
                tasks.append(aktivitaet_task)

            # Meilensteine der Phase als Tasks hinzufügen
            meilensteine = Meilenstein.query.filter_by(projektphase_id=phase.id).all()
            for meilenstein in meilensteine:
                meilenstein_datum = datetime.combine(meilenstein.datum, datetime.min.time())  # Umwandlung in datetime.datetime

                meilenstein_task = {
                    "id": f"meilenstein_{meilenstein.id}",
                    "name": meilenstein.name,
                    "start": meilenstein_datum.isoformat(),
                    "end": meilenstein_datum.isoformat(),  # Meilensteine haben keine Dauer
                    "progress": 0,  # Meilensteine haben keinen Fortschritt
                    "dependencies": f"phase_{phase.id}",  # Abhängigkeit von der übergeordneten Phase
                    "custom_class": "meilenstein-task",  # Optional: CSS-Klasse für Meilensteine
                    "is_milestone": True  # Markierung als Meilenstein
                }
                tasks.append(meilenstein_task)

        # Gantt-Daten zurückgeben
        return jsonify({
            "tasks": tasks,
            "project": {
                "id": projekt.id,
                "name": projekt.projekttitel,
                "start": projekt.startdatum_geplant.isoformat(),
                "end": projekt.enddatum_geplant.isoformat()
            }
        })