"""A Python Flask REST API BoilerPlate (CRUD) Style"""

import argparse
import os
from flask import Flask, jsonify, make_response
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
from routes.auth import AUTH_REQUEST
from routes.proprietaire import PROP_REQUEST
from routes.locataire import SERVICES_REQUEST
from routes.demarcheur import DEMARCHEUR_
from routes.admin import ADMIN
from routes.town_city_district import TCD
from routes.users import USERS_
from routes.appart import APPART_REQUEST

APP = Flask(__name__)

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Seans-Python-Flask-REST-Boilerplate"
    }
)
APP.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)
### end swagger specific ###


APP.register_blueprint(AUTH_REQUEST, url_prefix='/auth')
APP.register_blueprint(PROP_REQUEST, url_prefix='/proprietaire')
APP.register_blueprint(SERVICES_REQUEST, url_prefix='/locataire')
APP.register_blueprint(DEMARCHEUR_, url_prefix='/demarcheur')
APP.register_blueprint(ADMIN, url_prefix='/admin')
APP.register_blueprint(TCD, url_prefix='/tcd')
APP.register_blueprint(USERS_, url_prefix='/user')
APP.register_blueprint(APPART_REQUEST, url_prefix='/appart')

if __name__ == '__main__':

    PARSER = argparse.ArgumentParser(
        description="Seans-Python-Flask-REST-Boilerplate")

    PARSER.add_argument('--debug', action='store_true',
                        help="Use flask debug/dev mode with file change reloading")
    ARGS = PARSER.parse_args()

    PORT = int(os.environ.get('PORT', 5001))
    CORS = CORS(APP, resources={r"/*": {'origins':"*"}})
    if ARGS.debug:
        print("Running in debug mode")
        APP.run(host='0.0.0.0', port=PORT, debug=True)
    else:
        APP.run(host='0.0.0.0', port=PORT, debug=False)
