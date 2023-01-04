"""The Endpoints to manage the BOOK_REQUESTS"""
from .required_packages import (Blueprint, request, jsonify, ObjectId, json, _key, get_auth_token, datetime)
from .required_packages import decode_auth_token, get_user_info, datetime, cloudinary
from .required_packages import (APPARTEMENTS, USERS, DEMARCHEURS_REQUETS)
from bson import json_util
import random
import string
import os



PROP_REQUEST = Blueprint('proprietaire', __name__)

@PROP_REQUEST.route('/appart/new', methods=['POST'])
def add():
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

        if not request.get_json():
            return json.dumps({"data": "No data in request","status" : "KO"}, indent = 2, default=json_util.default),  400

        data = request.get_json()
        appart_id = str(ObjectId())
        appart = {
            "appart_id": appart_id,
            "demarcheur_id":_key(data, "demarcheur_id")[1],
            "owner_id": user_id,
            "caption":data["caption"],
            "country":data["country"],
            "town":data["town"],
            "district":data["district"],
            "description":data["description"],
            "specifications":data["specifications"],
            "price":int(data["price"]),
            "is_occupied":False,
            "certified":False,
            "rent":data["rent"],
            "corent":data["corent"],
            "interested_in_co_renting":[],
            "creation_date": datetime.datetime.now()
        }
        APPARTEMENTS.insert_one(appart)
        return json.dumps({"status": "success", "message": "appart was created successfully", "appart_id": appart_id}, indent = 2, default=json_util.default), 201

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2, default=json_util.default),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2, default=json_util.default),400


@PROP_REQUEST.route('/appart/update', methods=['POST'])
def update():
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

        if not request.get_json():
            return json.dumps({
                "data": "No data in request",
                "status" : "KO"
            }, indent = 2, default=json_util.default),  400

        data = request.get_json()
        old_appart = APPARTEMENTS.find_one({"appart_id": data["appart_id"], "owner_id": user_id})
        if not old_appart:
            return json.dumps({"status": "error", "message": "appart not find"}, indent = 2, default=json_util.default),400
        for key, detail in data.items():
            if key != "certified":
                old_appart[key] = detail
        APPARTEMENTS.find_one_and_update({"appart_id": data["appart_id"], "owner_id": user_id}, {"$set": old_appart})
        return json.dumps({"status": "success", "message": "appart was updated successfully"}, indent = 2, default=json_util.default), 201

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2, default=json_util.default),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2, default=json_util.default),400

@PROP_REQUEST.route('/appart/remove', methods=['DELETE'])
def remove():
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

        args = request.args
        data = args.to_dict()
        appart = APPARTEMENTS.find_one({"appart_id": data["appart_id"]})

        if not appart:
            return json.dumps({"status": "error", "message": "Appart not find"}, indent = 2, default=json_util.default),400

        APPARTEMENTS.find_one_and_delete({"appart_id": data["appart_id"]})
        return json.dumps({"status": "success", "message": "appart was deleted successfully"}, indent = 2, default=json_util.default), 202

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2, default=json_util.default),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2, default=json_util.default),400

@PROP_REQUEST.route('/appart/all', methods=['GET'])
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

        all_apparts = APPARTEMENTS.find({"owner_id": user_id})
        data = []
        for one_appart in all_apparts:
            if "_id" in one_appart:
                del one_appart["_id"]
            # tmp = {
            #     'appart_id': one_appart["appart_id"],
            #     'demarcheur_id': one_appart["demarcheur_id"],
            #     'owner_id': one_appart["owner_id"],
            #     'caption': one_appart["caption"],
            #     'country': one_appart["country"],
            #     'town': one_appart["town"],
            #     'district': one_appart["district"],
            #     'description': one_appart["description"],
            #     'specifications': one_appart["specifications"],
            #     'price': one_appart["price"],
            #     'is_occupied': one_appart["is_occupied"],
            #     'rent': one_appart["rent"],
            #     'certified': one_appart["certified"],
            #     'certified': one_appart["certified"],
            #     'co-rent': one_appart["co-rent"],
            #     'interested_in_co_renting': one_appart["interested_in_co_renting"],
            #     "creation_date": one_appart["creation_date"]
            # }
            data.append(one_appart)
        return json.dumps({"status": "success", "message": "appart research", "apparts": data, "total": len(data)}, indent = 2, default=json_util.default), 202

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2, default=json_util.default),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2, default=json_util.default),400

@PROP_REQUEST.route('/appart/detail', methods=['POST'])
def get_detail():
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

        if not request.get_json():
            return json.dumps({"data": "No data in request","status" : "KO"}, indent = 2, default=json_util.default),  400

        data = request.get_json()

        appart = APPARTEMENTS.find_one({"owner_id": user_id, "appart_id": data["appart_id"]})
        if not appart:
            return json.dumps({"status": "error", "message": "appart not find"}, indent = 2, default=json_util.default),400
        del appart["_id"]
        # appart_data = {
        #     'appart_id': appart["appart_id"],
        #     'demarcheur_id': appart["demarcheur_id"],
        #     'owner_id': appart["owner_id"],
        #     'caption': appart["caption"],
        #     'country': appart["country"],
        #     'town': appart["town"],
        #     'district': appart["district"],
        #     'description': appart["description"],
        #     'specifications': appart["specifications"],
        #     'price': appart["price"],
        #     'certified': appart["certified"],
        #     'is_occupied': appart["is_occupied"],
        #     'rent': appart["rent"],
        #     'co-rent': appart["co-rent"],
        #     'interested_in_co_renting': appart["interested_in_co_renting"],
        #     "creation_date": appart["creation_date"]
        #     }
        return json.dumps({"status": "success", "message": "appart research", "details": appart}, indent = 2, default=json_util.default), 202

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2, default=json_util.default),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2, default=json_util.default),400


@PROP_REQUEST.route('/appart/ask/demarcheur', methods=['POST'])
def ask_demarcheur():
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

        if not request.get_json():
            return json.dumps({"data": "No data in request","status" : "KO"}, indent = 2, default=json_util.default),  400

        data = request.get_json()

        detail = USERS.find_one({"user_id": data["demarcheur_id"], "role" : "demarcheur"})
        if not detail:
            return json.dumps({"status": "error", "message": "demarcheur  not find"}, indent = 2, default=json_util.default),400

        appart = APPARTEMENTS.find_one({"appart_id": data["appart_id"]})
        if not appart:
            return json.dumps({"status": "error", "message": "appart  not find"}, indent = 2, default=json_util.default),400
        old_request = DEMARCHEURS_REQUETS.find_one({"appart_id": data["appart_id"], "demarcheur_id": data["demarcheur_id"]})
        if old_request:
            return json.dumps({"status": "success", "message": "request already take into account"}, indent = 2, default=json_util.default),202

        myRequest = {
            "request_id": str(ObjectId()),
            "appart_id": data["appart_id"],
            "owner_id": user["user_id"],
            "owner_fname": user["firstname"],
            "owner_sname": user["surname"],
            "demarcheur_id":data["demarcheur_id"],
            "answer": "pending",
            "creation_date": datetime.datetime.now(),
            "exp_date": datetime.datetime.now()
        }
        DEMARCHEURS_REQUETS.insert_one(myRequest)
        return json.dumps({"status": "success", "message": "request accepted"}, indent = 2, default=json_util.default), 201

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2, default=json_util.default),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2, default=json_util.default),400

@PROP_REQUEST.route('/appart/add/images', methods=['POST'])
def add_images():
    array_links = []
    try:
        # auth_token = get_auth_token()
        # if not auth_token:
        #     return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2, default=json_util.default),400

        # d_token = decode_auth_token(auth_token)

        # if not d_token[0]:
        #     return json.dumps({"status": "error", "message": d_token[1]}, indent = 2, default=json_util.default),400

        # user_id = d_token[1]
        # user = get_user_info(user_id)
        # if user["role"] != "proprietaire":
        #     return json.dumps({"status": "error", "message": "access denied"}, indent = 2, default=json_util.default),403

        if len(request.files) == 0:
            return json.dumps({"data": "No data in request","status" : "KO"}, indent = 2, default=json_util.default),  400
        r_string = ''.join(random.choices(string.ascii_uppercase + string.ascii_lowercase, k=5))
        data = request.files
        files = data.to_dict(flat=False)
        temp_link = f'public/appart_images/image-yl-{r_string}.{files["image"][0].filename.split(".")[-1]}'
        files["image"][0].save(temp_link)
        cloudinary.uploader.upload(temp_link, public_id=f"public/appart_images/image-yl-{r_string}", unique_filename = True, overwrite=False)
        srcURL = cloudinary.CloudinaryImage(f"public/appart_images/image-yl-{r_string}.{files['image'][0].filename.split('.')[-1]}").build_url()
        os.remove(temp_link)
        return json.dumps({"status": "success", "message": "image uploaded", "link": srcURL}, indent = 2, default=json_util.default), 200

    except KeyError as error:
        print(error)
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2, default=json_util.default),400
    except Exception as error:
        print(error)
        return json.dumps({"status": "error", "message": str(error)}, indent = 2, default=json_util.default),400
