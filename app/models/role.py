from app import db

class Role(db.Document):
    name = db.StringField(required=True, unique=True)

    @staticmethod
    def initialize_roles():
        for role_name in ['admin', 'seller', 'user']:
            if not Role.objects(name=role_name):
                Role(name=role_name).save()
