from .required_packages import (Blueprint, request, jsonify, ObjectId, json, _key, get_auth_token, datetime)
from .required_packages import decode_auth_token, get_user_info, is_demarcheur, is_admin
from .required_packages import (APPARTEMENTS, USERS, DEMARCHEURS_REQUETS, TOKENS)
from bson import json_util

ADMIN = Blueprint('admin', __name__)

@ADMIN.route('/users/all/', methods=['GET'])
def users_all():
    try:
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400

        d_token = decode_auth_token(auth_token)

        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        user_id = d_token[1]
        dem = is_admin(user_id)
        if not dem:
            return json.dumps({"status": "error", "message": "access denied"}, indent = 2),403

        all_users = []
        args = request.args
        data = args.to_dict()

        if not ("locataire" in data):
            return jsonify({"status" : "error","message" : "locataire state is required"}), 400
        if not ("demarcheur" in data):
            return jsonify({"status" : "error","message" : "demarcheur state is required"}), 400
        if not ("proprietaire" in data):
            return jsonify({"status" : "error","message" : "proprietaire state is required"}), 400

        if (data["locataire"].lower() == "true"):
            users = USERS.find({"role": "locataire"})
            if users:
                for user in users:
                    tmp = {
                        "user_id": user["user_id"],
                        "firstname": user["firstname"],
                        "surname": user["surname"],
                        "phone": user["phone"],
                        "role": user["role"],
                        "country": user["country"],
                        "town": user["town"],
                        "district": user["district"],
                        "email": user["email"]
                    }
                    all_users.append(tmp)

        if (data["proprietaire"].lower() == "true"):
            users = USERS.find({"role": "proprietaire"})
            if users:
                for user in users:
                    tmp = {
                        "user_id": user["user_id"],
                        "firstname": user["firstname"],
                        "surname": user["surname"],
                        "phone": user["phone"],
                        "role": user["role"],
                        "country": user["country"],
                        "town": user["town"],
                        "district": user["district"],
                        "email": user["email"]
                    }
                    all_users.append(tmp)
        if (data["demarcheur"].lower() == "true"):
            users = USERS.find({"role": "demarcheur"})
            if users:
                for user in users:
                    tmp = {
                        "user_id": user["user_id"],
                        "firstname": user["firstname"],
                        "surname": user["surname"],
                        "phone": user["phone"],
                        "role": user["role"],
                        "country": user["country"],
                        "town": user["town"],
                        "district": user["district"],
                        "email": user["email"]
                    }
                    all_users.append(tmp)
        if (data["demarcheur"].lower() == "false") and (data["proprietaire"].lower() == "false") and (data["locataire"].lower() == "false"):
            all_users = []
            users = USERS.find()
            if users:
                for user in users:
                    tmp = {
                        "user_id": user["user_id"],
                        "firstname": user["firstname"],
                        "surname": user["surname"],
                        "phone": user["phone"],
                        "role": user["role"],
                        "country": user["country"],
                        "town": user["town"],
                        "district": user["district"],
                        "email": user["email"]
                    }
                    all_users.append(tmp)
        return json.dumps({"status": "success", "message": "get all users", "users": all_users, "total": len(all_users)}, indent = 2, default=str), 201

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2),400

@ADMIN.route('/apparts/all/', methods=['GET'])
def apparts_all():
    try:
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400

        d_token = decode_auth_token(auth_token)

        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        user_id = d_token[1]
        dem = is_admin(user_id)
        if not dem:
            return json.dumps({"status": "error", "message": "access denied"}, indent = 2),403

        all_apparts = []
        args = request.args
        data = args.to_dict()

        all_apparts = []
        apparts = APPARTEMENTS.find()
        if apparts:
            for appart in apparts:
                tmp = {
                    "appart_id": appart["appart_id"],
                    "demarcheur_id":appart["demarcheur_id"],
                    "owner_id": appart["owner_id"],
                    "caption":appart["caption"],
                    "country":appart["country"],
                    "town":appart["town"],
                    "district":appart["district"],
                    "description":appart["description"],
                    "specifications":appart["specifications"],
                    "price":appart["price"],
                    "is_occupied":appart["is_occupied"],
                    "certified":appart["certified"],
                    "rent":appart["rent"],
                    "co-rent":appart["co-rent"],
                    "interested_in_co_renting":["interested_in_co_renting"]
                }
                all_apparts.append(tmp)
        return json.dumps({"status": "success", "message": "get all apparts", "apparts": all_apparts, "total": len(all_apparts)}, indent = 2, default=str), 201

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2),400


@ADMIN.route('/appart/certificate', methods=['POST'])
def certificate():
    try:
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400

        d_token = decode_auth_token(auth_token)

        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        user_id = d_token[1]
        adm = is_admin(user_id)
        if not adm:
            return json.dumps({"status": "error", "message": "access denied"}, indent = 2),403

        if not request.get_json():
            return json.dumps({"data": "No data in request","status" : "KO"}, indent = 2),  400

        data = request.get_json()

        my_request = APPARTEMENTS.find_one({"appart_id": data["appart_id"]})
        if not my_request:
            return json.dumps({"status": "error", "message": "appart not find"}, indent = 2),404

        if data["certified"] == True:
            my_request = APPARTEMENTS.find_one_and_update({"appart_id": data["appart_id"]},  {"$set": {"certified": True}})
            return json.dumps({"status": "success", "message": "you just certified an appart"}, indent = 2, default=str), 201
        if data["certified"] == False:
            my_request = APPARTEMENTS.find_one_and_update({"appart_id": data["appart_id"]},  {"$set": {"certified": False}})
            return json.dumps({"status": "success", "message": "you just uncertified an appart"}, indent = 2, default=str), 201

        return json.dumps({"status": "error", "message": "bad answer"}, indent = 2),403

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2),400
