from app import db
import enum
from sqlalchemy import Enum

class PrioritaetEnum(enum.Enum):
    Niedrig = "Niedrig"
    Mittel = "Mittel"
    Hoch = "Hoch"

class ProjektStatusEnum(enum.Enum):
    Geplant = "Geplant"
    InBearbeitung = "In Bearbeitung"
    Pausiert = "Pausiert"
    Abgeschlossen = "Abgeschlossen"
    Abgebrochen = "Abgebrochen"

class VorgehensmodellEnum(enum.Enum):
    Wasserfall = "Wasserfall"
    Agil = "Agil"
    Hybrid = "Hybrid"

class KostenartEnum(enum.Enum):
    Hardware = "Hardware"
    Software = "Software"
    Dienstleistungen = "Dienstleistungen"
    Reisespesen = "Reisespesen"
    Unterkunft = "Unterkunft"
    Nachbesserung = "Nachbesserung"

class RessourceFunktion(enum.Enum):
    Projektleiter = "Projektleiter"
    Projektmitarbeiter = "Projektmitarbeiter"
    Architekt = "Architekt"
    Entwickler = "Entwickler"
    Tester = "Tester"
    BusinessAnalyst = "Business Analyst"
    PrductOwner = "Product Owner"
    ScrumMaster = "Scrum Master"
    Designer = "Designer"
    QualitaetsSicherung = "Qualitätssicherung"
    Dokumentation = "Dokumentation"
    Stakeholder = "Stakeholder"
    Kunde = "Kunde"

class Projekt(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projekttitel = db.Column(db.String(255), nullable=False)
    projektbeschreibung = db.Column(db.Text, nullable=True)
    bewilligungsdatum = db.Column(db.Date, nullable=False)

    prioritaet = db.Column(Enum(PrioritaetEnum), nullable=False, default=PrioritaetEnum.Mittel)
    status = db.Column(Enum(ProjektStatusEnum), nullable=False, default=ProjektStatusEnum.Geplant)
    vorgehensmodell = db.Column(Enum(VorgehensmodellEnum), nullable=False, default=VorgehensmodellEnum.Hybrid)

    startdatum_geplant = db.Column(db.Date, nullable=False)
    enddatum_geplant = db.Column(db.Date, nullable=False)
    startdatum_effektiv = db.Column(db.Date, nullable=True)
    enddatum_effektiv = db.Column(db.Date, nullable=True)
    fortschritt = db.Column(db.Float, nullable=True)
    projektleiter_id = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)


class Projektphase(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projekt_id = db.Column(db.Integer, db.ForeignKey('projekt.id'), nullable=False)
    phase_name = db.Column(db.String(255), nullable=True)
    startdatum_geplant = db.Column(db.Date, nullable=False)
    enddatum_geplant = db.Column(db.Date, nullable=False)
    startdatum_effektiv = db.Column(db.Date, nullable=True)
    enddatum_effektiv = db.Column(db.Date, nullable=True)
    reviewdatum_geplant = db.Column(db.Date, nullable=True)
    reviewdatum_effektiv = db.Column(db.Date, nullable=True)
    freigabedatum = db.Column(db.Date, nullable=True)
    freigabevisum = db.Column(db.String(255), nullable=True)
    fortschritt = db.Column(db.Float, nullable=True)
    
    status = db.Column(Enum(ProjektStatusEnum), nullable=False, default=ProjektStatusEnum.Geplant)
    meilensteine = db.relationship('Meilenstein', backref='projektphase', cascade="all, delete")
    aktivitaeten = db.relationship('Aktivitaet', backref='projektphase', cascade="all, delete")
    dokumente = db.relationship('Dokument', backref='projektphase', cascade="all, delete")

class Meilenstein(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projekt_id = db.Column(db.Integer, db.ForeignKey('projekt.id'), nullable=False)
    projektphase_id = db.Column(db.Integer, db.ForeignKey('projektphase.id'), nullable=True)
    name = db.Column(db.String(255), nullable=False)
    datum = db.Column(db.Date, nullable=False)

class Aktivitaet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    projektphase_id = db.Column(db.Integer, db.ForeignKey('projektphase.id'), nullable=False)
    name = db.Column(db.String(255), nullable=False)
    beschreibung = db.Column(db.Text, nullable=True)
    startdatum_geplant = db.Column(db.Date, nullable=False)
    enddatum_geplant = db.Column(db.Date, nullable=False)
    startdatum_effektiv = db.Column(db.Date, nullable=True)
    enddatum_effektiv = db.Column(db.Date, nullable=True)
    budget = db.Column(db.Float, nullable=True)
    effektive_kosten = db.Column(db.Float, nullable=True)
    fortschritt = db.Column(db.Float, nullable=True)
    
    ressourcen = db.Column(db.Integer, db.ForeignKey('person.id'), nullable=False)
    rolle = db.Column(Enum(RessourceFunktion), nullable=True)
    auslastung = db.Column(db.Float, nullable=True)
    externe_kosten = db.relationship('ExterneKosten', backref='aktivitaet', cascade="all, delete")
    rapport = db.relationship('Rapport', backref='aktivitaet', cascade="all, delete")


class ExterneKosten(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aktivitaet_id = db.Column(db.Integer, db.ForeignKey('aktivitaet.id'), nullable=False)
    kostenart = db.Column(db.String(255), nullable=False)
    budgetiert = db.Column(db.Float, nullable=False)
    effektiv = db.Column(db.Float, nullable=True)
    abweichung = db.Column(db.Float, nullable=True)
    begruendung = db.Column(db.String(255), nullable=True)

class Rapport(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    aktivitaet_id = db.Column(db.Integer, db.ForeignKey('aktivitaet.id'), nullable=False)
    datum = db.Column(db.Date, nullable=False)
    titel = db.Column(db.String(255), nullable=False)
    kommentar = db.Column(db.String(255), nullable=True)
    aufwand_stunden = db.Column(db.Float, nullable=False)
    material_kosten = db.Column(db.Float, nullable=False)
    verbrauchtes_material = db.Column(db.String(255), nullable=True)
    kostenart = db.Column(Enum(KostenartEnum), nullable=True)

class Dokument(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    dokumentenname = db.Column(db.String(255), nullable=False)
    dateipfad = db.Column(db.String(255), nullable=False)
    typ = db.Column(db.String(255), nullable=False)
    hochladedatum = db.Column(db.Date, nullable=False)
    projekt_id = db.Column(db.Integer, db.ForeignKey('projekt.id'), nullable=True)
    projektphase_id = db.Column(db.Integer, db.ForeignKey('projektphase.id'), nullable=True)
    aktivitaet_id = db.Column(db.Integer, db.ForeignKey('aktivitaet.id'), nullable=True)