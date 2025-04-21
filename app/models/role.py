from app import db

class Role(db.Document):
    name = db.StringField(required=True, unique=True)

    @staticmethod
    def initialize_roles():
        if not Role.objects(name='admin'):
            Role(name='admin').save()
        if not Role.objects(name='seller'):
            Role(name='seller').save()
        if not Role.objects(name='user'):
            Role(name='user').save()
