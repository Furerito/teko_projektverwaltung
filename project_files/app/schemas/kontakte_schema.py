# schemas/kontakte_schema.py
from app import ma
from app.models.kontakte_model import Person

class PersonSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Person
        load_instance = True