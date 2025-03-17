from app import ma
from app.models.users_model import *

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Users
        load_instance = True

