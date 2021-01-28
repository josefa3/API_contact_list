"""
This module takes care of starting the API Server, Loading the DB and Adding the endpoints
"""
import os
from flask import Flask, request, jsonify, url_for
from flask_migrate import Migrate
from flask_swagger import swagger
from flask_cors import CORS
from utils import APIException, generate_sitemap
from admin import setup_admin
from models import db, Contact
#from models import Person

app = Flask(__name__)
app.url_map.strict_slashes = False
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DB_CONNECTION_STRING')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
MIGRATE = Migrate(app, db)
db.init_app(app)
CORS(app)
setup_admin(app)

# Handle/serialize errors like a JSON object
@app.errorhandler(APIException)
def handle_invalid_usage(error):
    return jsonify(error.to_dict()), error.status_code

# generate sitemap with all your endpoints
@app.route('/')
def sitemap():
    return generate_sitemap(app)

@app.route('/contact', methods=['GET'])
def handle_contacts():
    contacts = Contact.query.all()
    response_body = []
    for contact in contacts:
        response_body.append(contact.serialize()) #serialize pasa un diccionario
    return jsonify(response_body), 200

@app.route('/contact', methods=['POST'])
def add_new_contact():
    # First we get the payload json
    body = request.get_json()
    if body is None:
        raise APIException("You need to specify the request body as a json object", status_code=400)
    if 'full_name' not in body:
        raise APIException('You need to specify the username', status_code=400)
    if 'email' not in body:
        raise APIException('You need to specify the email', status_code=400)
    if 'address' not in body:
        raise APIException('You need to specify the address', status_code=400)
    if 'phone' not in body:
        raise APIException('You need to specify the phone', status_code=400)
    # at this point, all data has been validated, we can proceed to inster into the bd
    new_contact = Contact(full_name=body['full_name'], email=body['email'], address=body['address'], phone=['phone']) #pasamos los parametros
    db.session.add(new_contact) # añade un contacto en la base de datos, lo deja en cola
    try:
       db.session.commit() # intentas que se integre el cambio
       return jsonify(new_contact.serialize()), 201
    except Exception as error:
        print(error.args) 
        return jsonify("NOT OK"), 500

@app.route('/contact/<contact_id>', methods=['PUT', 'GET'])
def get_single_contact(id):
    """
    Single person
    """
    body = request.get_json()
    if request.method == 'PUT':
        contact = Contact.query.get(id)
        if contact is None:
            raise APIException('Contact not found', status_code=404)
        if "full_name" in body:
            contact.full_name = body["full_name"]
        if "email" in body:
            contact.email = body["email"]
        if "address" in body:
            contact.address = body['address'] 
        if "phone" in phone:
            contact.phone = body['phone']
        db.session.commit()
        return jsonify(contact.serialize()), 200
    if request.method == 'GET':
        contact = Contact.query.get(id)
        return jsonify(contact.serialize()), 200

    return "Invalid Method", 404

@app.route('/contact/<contact_id>', methods=['DELETE'])
def delete_contact(id):
    contact = Contact.query.get(id)
    if contact is None:
        raise APIException('Contact not found', status_code=404)
    db.session.delete(contact)
    db.session.commit()

# this only runs if `$ python src/main.py` is executed
if __name__ == '__main__':
    PORT = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=PORT, debug=False)
