import uuid
from datetime import datetime, timedelta
from flask import jsonify, abort, request, Blueprint
from validate_email import validate_email
from pymongo import MongoClient
import bcrypt
from bson.objectid import ObjectId
import jwt, json
import datetime
from bson import json_util
import cloudinary
import cloudinary.uploader
import cloudinary.api

client = MongoClient("mongodb+srv://yemalin-location:0J4JpSHCZCOYRRRw@yemalin-location.9ffbggd.mongodb.net/")
db = client["yemalin-location"]
USERS = db["users"]
TOKENS = db["tokens"]
CREDS = db["creds"]
APPARTEMENTS = db["appartements"]
GROUPS = db["groups"]
DEMARCHEURS_REQUETS = db["demarcheurs_requests"]
ToCiDi = db["tcd"]
salt = CREDS.find_one({"type": "salt"})['salt']
cloudinary.config(
    cloud_name = "ddvdir4ab",
    api_key = "315297728627154",
    api_secret = "YXDeDdSX2Ws2YDbWr5Ckpy6EWdc",
    secure = True
)

def encoded_jwt_token(user_id):
    encoded_jwt = jwt.encode({"user_id": user_id}, "secret", algorithm="HS256")
    return (encoded_jwt)

def get_auth_token():
    auth_token = request.headers.get('Authorization')
    if auth_token is not None:
        auth_token = auth_token.split()[1]
        print(auth_token)
        return auth_token
    else:
        print("None")
        return None

def decode_auth_token(auth_token):
    try:
        payload = jwt.decode(auth_token, "secret", algorithms=["HS256"])
        fr = TOKENS.find_one({"user_id": payload['user_id']})
        if fr is None:
            return False, 'Invalid token. Please log in again.'
        return True, payload['user_id'] #renverra un tuple contenant (True, user_id)
    except jwt.ExpiredSignatureError:
        return False, 'Signature expired. Please log in again.'
    except jwt.InvalidTokenError:
        return False, 'Invalid token. Please log in again.'

def get_user_info(user_id):
    user = USERS.find_one({"user_id": user_id})
    if not user:
        return False, None
    return user


def _key(data, key):
    try:
        data[key]
        return True, data[key]
    except:
        return False, ""

def IsValidToken(token, user_id):
    tok = TOKENS.find_one({"token" : token, "user_id" : user_id})

    if datetime.now() >= tok["exp_date"]:
        TOKENS.delete_one({"token" : token})
        return False
    return True

def is_demarcheur(user_id):
    try:
        user = USERS.find_one({"user_id": user_id})
        if user:
            if user["role"] != "demarcheur":
                return False
            return True
    except Exception:
        return False

def is_admin(user_id):
    try:
        user = USERS.find_one({"user_id": user_id})
        if user:
            if user["role"] != "admin":
                return False
            return True
    except Exception:
        return False

def is_proprietaire(user_id):
    try:
        user = USERS.find_one({"user_id": user_id})
        if user:
            if user["role"] != "proprietaire":
                return False
            return True
    except Exception:
        return False

def is_locataire(user_id):
    try:
        user = USERS.find_one({"user_id": user_id})
        if user:
            if user["role"] != "locataire":
                return False
            return True
    except Exception:
        return False


def generate_demarcheur_code(user_id):
    tokenTmp = {}
    # """ format for code is YEML-DEM-firstname+lastname+randomint"""
    try:
        # creation_date_time = datetime.datetime.now()
        # expiration_date_time = creation_date_time + timedelta(
        #     hours = 1*24        #la durée d'expiration dun token en heures
        # )
        # payload = {             #les information que le token doit stocker
        #     'exp': expiration_date_time,
        #     'iat': datetime.datetime.now(),
        #     'user': user_id
        # }
        # encodejwt_temp = jwt.encode(
        #     payload,
        #     "YEML-DEM-",
        #     algorithm='HS256'
        # )                       #le token généré (un string)
        user_info = get_user_info(user_id)
        encodejwt = "YEML-DEM-" + str(user_info["firstname"][:3]) + str(user_info["surname"][3:]) + str(user_id[:3]) + str(user_id[:2])
        tokenTmp['type'] = "demarcheur_code"
        tokenTmp['token'] = encodejwt
        tokenTmp['user_id'] = user_id
        TOKENS.insert_one(tokenTmp)
        return tokenTmp["token"]
    except Exception as e:
        return e