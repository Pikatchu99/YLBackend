"""The Endpoints to manage the BOOK_REQUESTS"""
from .required_packages import (Blueprint, request, json, bcrypt, USERS, salt, ObjectId, encoded_jwt_token, TOKENS, datetime, json, generate_demarcheur_code, get_auth_token, decode_auth_token)
from bson import json_util

AUTH_REQUEST = Blueprint('auth', __name__)

@AUTH_REQUEST.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    if not data :
        return json.dumps({
        "status": "error",
        "message": "No data sent"
    }, indent=2, default=json_util.default), 400
    try:
        phone = data["phone"]
        firstname = data["firstname"]
        surname = data["surname"]
        role = data["role"]
        email = data["email"]
        password = data["password"]

        country = ""
        town = ""
        district = ""

        if "country" in data :
            country = data["country"]
        if "town" in data :
            town = data["town"]
        if "district" in data:
            district = data["district"]

        #check if user exists
        if USERS.find_one({"email" : data["email"]}) or \
        USERS.find_one({"phone" : data["phone"]}):
            return json.dumps({

            "status": "error",
            "message": "Phone Number or Email adress aldready used" 
        }, indent=2, default=json_util.default), 400

        password = password.encode('utf8')
        hashed_password = bcrypt.hashpw(password, salt.encode('utf8'))
        user_id = str(ObjectId())
        token = encoded_jwt_token(user_id)

        new_account = {
            "user_id": user_id,
            "firstname": firstname,
            "surname": surname,
            "phone": phone,
            "role": role,
            "country": country,
            "town": town,
            "district": district,
            "email": email,
            "password": str(hashed_password)
        }

        USERS.insert_one(new_account)
        if role == "demarcheur":
            generate_demarcheur_code(user_id)
        TOKENS.insert_one({
            "user_id" : user_id, 
            "token" : token,
            "type" : "auth",
            "cre_date" : datetime.datetime.now(),
            "exp_date": datetime.datetime.now() + datetime.timedelta(days=1)
            })

        return json.dumps({
            "status": "success",
            "message": "Account created successfully",
            "token" : token,
            "firstname" : data["firstname"],
            "surname" : data["surname"],
            "phone" : data["phone"],
            "country": country,
            "town": town,
            "district": district,
            "role": data["role"],
            "email" : data["email"]
        }, indent=2, default=json_util.default), 201
    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong"
        }, indent=2, default=json_util.default), 400

@AUTH_REQUEST.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data :
        return json.dumps({
            "status": "error",
            "message": "No data sent" 
    }, indent=2, default=json_util.default), 400
    try:
        password = data["password"]
        password = password.encode('utf8')
        hashed_password = bcrypt.hashpw(password, salt.encode('utf8'))
        to_connect_email = {
            "email" : data["phone_email"],
            "password" : str(hashed_password)
        }
        to_connect_phone = {
            "phone" : data["phone_email"],
            "password" : str(hashed_password)
        }
        found = USERS.find_one(to_connect_email)
        if not found:
            found = USERS.find_one(to_connect_phone)
        if found:
            token = encoded_jwt_token(found["user_id"])
            TOKENS.delete_many({"user_id" : found["user_id"]})
            TOKENS.insert_one({
                "user_id" : found["user_id"], 
                "type": "auth",
                "token" : token,
                "cre_date": datetime.datetime.now(),
                "exp_date": datetime.datetime.now() + datetime.timedelta(days=1)
            })
            return json.dumps({
                "status": "success",
                "message": "User logged successfully",
                "token": token,
                "firstname" : found["firstname"],
                "surname" : found["surname"],
                "phone" : found["phone"],
                "country" : found["country"],
                "town" : found["town"],
                "district" : found["district"],
                "role": found["role"],
                "email" : found["email"]
        }, indent=2, default=json_util.default), 201

        return json.dumps({
            "status": "error",
            "message": "Bad credentials" 
        }, indent=2, default=json_util.default), 400
    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong" 
    }, indent=2, default=json_util.default), 400

@AUTH_REQUEST.route('/logout', methods=['POST'])
def logout():
    try:
        #token verif
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400
        d_token = decode_auth_token(auth_token)
        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400
        user_id = d_token[1]

        TOKENS.delete_one({"user_id": user_id, "token" : auth_token})
        return json.dumps({
            "status": "succes",
            "message": "Successfully logged out"
        }, indent=2, default=json_util.default), 201
    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong"
        }, indent=2, default=json_util.default), 400