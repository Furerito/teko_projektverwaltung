from app import ma
from app.models.projekte_model import *

class ProjektSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Projekt
        load_instance = True

class ProjektphaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Projektphase
        load_instance = True

class MeilensteinSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Meilenstein
        load_instance = True

class AktivitaetSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Aktivitaet
        load_instance = True

class ExterneKostenSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ExterneKosten
        load_instance = True

class RapportSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Rapport
        load_instance = True

class DokumentSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Dokument
        load_instance = True