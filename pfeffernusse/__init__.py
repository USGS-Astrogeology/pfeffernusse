import connexion
from pfeffernusse import encoder

application = connexion.App(__name__, specification_dir='./openapi/')
application.app.json_encoder = encoder.JSONEncoder
application.add_api('openapi.yaml', arguments={'title': 'Pfeffernusse'})
