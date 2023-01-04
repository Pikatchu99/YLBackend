"""The Endpoints to manage the BOOK_REQUESTS"""
from .required_packages import (Blueprint, request, json, get_auth_token, datetime)
from .required_packages import decode_auth_token, get_user_info, is_demarcheur, generate_demarcheur_code, _key
from .required_packages import (APPARTEMENTS, USERS, DEMARCHEURS_REQUETS, TOKENS)
from bson import json_util

DEMARCHEUR_ = Blueprint('demarcheur', __name__)

@DEMARCHEUR_.route('/request/all', methods=['GET'])
def all():
    try:
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400

        d_token = decode_auth_token(auth_token)

        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        user_id = d_token[1]
        dem = is_demarcheur(user_id)
        if not dem:
            return json.dumps({"status": "error", "message": "access denied"}, indent = 2),403
        my_request = DEMARCHEURS_REQUETS.find({"demarcheur_id": user_id, "answer": "pending"})
        data = []
        for i in my_request:
            if "_id" in i:
                del i["_id"]
            data.append(i)
        return json.dumps({"status": "success", "message": "get all request", "requests": data, "total": len(data)}, indent = 2, default=str), 201

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2),400

@DEMARCHEUR_.route('/request/answer', methods=['POST'])
def request_answer():
    try:
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400

        d_token = decode_auth_token(auth_token)

        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        user_id = d_token[1]
        dem = is_demarcheur(user_id)
        if not dem:
            return json.dumps({"status": "error", "message": "access denied"}, indent = 2),403

        if not request.get_json():
            return json.dumps({"data": "No data in request","status" : "KO"}, indent = 2),  400

        data = request.get_json()

        my_request = DEMARCHEURS_REQUETS.find_one({"demarcheur_id": user_id, "request_id": data["request_id"], "answer": "pending"})
        if not my_request:
            return json.dumps({"status": "error", "message": "request not found"}, indent = 2),404

        if data["answer"] == "accepted":
            my_request = DEMARCHEURS_REQUETS.find_one_and_update({"demarcheur_id": user_id, "request_id": data["request_id"], "answer": "pending"},  {"$set": {"answer": "accepted"}})
            APPARTEMENTS.find_one_and_update({"appart_id": my_request["appart_id"]},  {"$set": {"demarcheur_id": user_id}})
            return json.dumps({"status": "success", "message": "You got it"}, indent = 2, default=str), 201

        if data["answer"] == "rejected":
            my_request = DEMARCHEURS_REQUETS.find_one_and_update({"demarcheur_id": user_id, "request_id": data["request_id"], "answer": "pending"},  {"$set": {"answer": "rejected"}})
            return json.dumps({"status": "success", "message": "You reject demand"}, indent = 2, default=str), 201

        return json.dumps({"status": "error", "message": "bad answer"}, indent = 2),403

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
    except Exception as error:
        print(error)
        return json.dumps({"status": "error", "message": str(error)}, indent = 2),400

@DEMARCHEUR_.route('/appart/all', methods=['GET'])
def apart_all():
    try:
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400

        d_token = decode_auth_token(auth_token)

        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        user_id = d_token[1]
        dem = is_demarcheur(user_id)
        if not dem:
            return json.dumps({"status": "error", "message": "access denied"}, indent = 2),403

        my_request = APPARTEMENTS.find({"demarcheur_id": user_id})
        data = []
        for i in my_request:
            tmp = {
                'appart_id': i["appart_id"],
                'demarcheur_id': i["demarcheur_id"],
                'owner_id': i["owner_id"],
                'caption': i["caption"],
                'country': i["country"],
                'town': i["town"],
                'district': i["district"],
                'description': i["description"],
                'specifications': i["specifications"],
                'price': i["price"],
                'is_occupied': i["is_occupied"],
                'rent': i["rent"],
                'co-rent': i["co-rent"],
                'interested_in_co_renting': i["interested_in_co_renting"]
            }
            data.append(tmp)
        return json.dumps({"status": "success", "message": "get all appart", "apparts": data, "total": len(data)}, indent = 2, default=str), 201

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2),400

@DEMARCHEUR_.route('/invitation/appart/all', methods=['GET'])
def invitation_appart_all():
    try:
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400

        d_token = decode_auth_token(auth_token)

        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        user_id = d_token[1]

        args = request.args
        data = args.to_dict()


        if not _key(data, "demarcheur_code")[0]:
            return json.dumps({"status": "error", "message": "Please provide demarcheur code"}, indent = 2),400

        demarcheur_code = data["demarcheur_code"]

        demarcheur_user_id = TOKENS.find_one({"type": "demarcheur_code", "token": demarcheur_code})

        if not demarcheur_user_id:
            return json.dumps({"status": "error", "message": "Demarcheur not found"}, indent = 2),400

        demarcheur_appart_all = APPARTEMENTS.find({"demarcheur_id": demarcheur_user_id["user_id"]})
        to_return_appart_all = []

        for ap in demarcheur_appart_all:
            del ap["_id"]
            to_return_appart_all.append(ap)

        return json.dumps({"status": "success", "message": "get demarcheur appart", "apparts": to_return_appart_all}, indent = 2, default=json_util.default),201
    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2),400


@DEMARCHEUR_.route('/all', methods=['GET'])
def get_all():
    try:
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2, default=json_util.default),400

        d_token = decode_auth_token(auth_token)

        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2, default=json_util.default),400

        user_id = d_token[1]
        user = get_user_info(user_id)
        if user["role"] != "proprietaire":
            return json.dumps({"status": "error", "message": "access denied"}, indent = 2, default=json_util.default),403

        all_demarcheurs = USERS.find({"role": "demarcheur"})
        data = []
        for one_appart in all_demarcheurs:
            if "_id" in one_appart:
                del one_appart["_id"]
            if "password" in one_appart:
                del one_appart["password"]
            data.append(one_appart)
        return json.dumps({"status": "success", "message": "all demarcheur", "demarcheurs": data, "total": len(data)}, indent = 2, default=json_util.default), 202

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2, default=json_util.default),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2, default=json_util.default),400


@DEMARCHEUR_.route('/invitation/code', methods=['GET'])
def invitation():
    try:
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400

        d_token = decode_auth_token(auth_token)

        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        user_id = d_token[1]
        dem = is_demarcheur(user_id)
        if not dem:
            return json.dumps({"status": "error", "message": "access denied"}, indent = 2),403
        code = TOKENS.find_one({"type": "demarcheur_code", "user_id": user_id})
        if code:
            return json.dumps({"status": "success", "message": "code", "code": code["token"]}, indent = 2),201
        if not code:
            my_code = generate_demarcheur_code(user_id)
        return json.dumps({"status": "success", "message": "code", "code": my_code}, indent = 2),201

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2),400

