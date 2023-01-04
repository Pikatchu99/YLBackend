from .required_packages import (Blueprint, request, json, APPARTEMENTS, get_auth_token, get_auth_token, decode_auth_token, GROUPS, ObjectId)
from .required_packages import _key, get_user_info
from bson import json_util
import time

SERVICES_REQUEST = Blueprint('locataire', __name__)

@SERVICES_REQUEST.route('/appart/all', methods=['GET'])
def all():
    try:
        to_return = []
        result = APPARTEMENTS.find().sort("creation_date", -1)
        for i in result:
            if '_id' in i:
                del i['_id']
            to_return.append(i)
        return json.dumps({
            "status": "success",
            "message": "get all appart",
            "data": to_return,
            "total": len(to_return)
            }, indent=2, default=json_util.default), 201
    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong"
        }, indent=2, default=json_util.default), 400


@SERVICES_REQUEST.route('/appart/search', methods=['POST'])
def search():
    try:
        data = request.get_json()
        query = {}

        if _key(data, "country")[0]  and _key(data, "country")[1] != "":
            query["country"] = _key(data, "country")[1]
        if _key(data, "town")[0]  and _key(data, "town")[1] != "":
            query["town"] = _key(data, "town")[1]
        if _key(data, "district")[0]  and _key(data, "district")[1] != "":
            query["district"] = _key(data, "district")[1]
        if _key(data, "specifications")[0]:
            values = {k: v for k, v in data["specifications"].items() if v}
            if len(values) > 0:
                for key, value in values.items():
                    query["specifications."+key] = value
        if _key(data, "min_price")[0] and _key(data, "min_price")[1] != "":
            query["price"] = {"$gte" : int(_key(data, "min_price")[1])}
        if _key(data, "max_price")[0] and _key(data, "max_price")[1] != "":
            query["price"] = {"$lte" : int(_key(data, "max_price")[1]) }
        print(query)

        to_return = []
        result = APPARTEMENTS.find(query).sort("creation_date", -1)
        for i in result:
            to_return.append(i)
        if to_return == []:
            return json.dumps({
                "status": "success",
                "message": "No appart found",
                "data": []
                }, indent=2, default=json_util.default), 404

        else:
            for i in to_return:
                del i['_id']
            return json.dumps({
                "status": "success",
                "message": "search appart",
                "data": to_return,
                "total": len(to_return),
            }, indent=2, default=json_util.default), 200

    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong"
        }, indent=2, default=json_util.default), 400

@SERVICES_REQUEST.route('/appart/group/create', methods=['POST'])
def create():
    try:
        #token verif
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400
        d_token = decode_auth_token(auth_token)
        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        data = request.get_json()
        if not data :
            return json.dumps({
            "status": "error",
            "message": "No data sent"
        }, indent=2, default=json_util.default), 400


        user_id = d_token[1]
        appart_id = data["appart_id"]
        #check if user in group
        check = GROUPS.find()
        test = None
        for i in check:
            if user_id in i["members"]:
                test = user_id

        if test:
            return json.dumps({
            "status": "error",
            "message": "User already in group, please delete your group or leave a group"
        }, indent=2, default=json_util.default), 400

        appart = APPARTEMENTS.find_one({"appart_id": appart_id})
        nb_place = appart["specifications"]["room"]

        test = GROUPS.find().limit(1).sort([('$natural',-1)])
        if test:
            pos = 0
        else:
            pos = test["position"] + 1
        in_group = [user_id]
        user_info = get_user_info(user_id)
        if _key(data, "groupe_name")[0]:
            group_name = data["groupe_name"]
            check = GROUPS.find_one({"name": group_name})
            if check:
                return json.dumps({
                "status": "error",
                "message": "Name already exist, please choose another name"
            }, indent=2, default=json_util.default), 400

        if not _key(data, "groupe_name")[0]:
            group_name = "Groupe de " + user_info["firstname"] + " " + user_info["surname"]
        GROUPS.insert_one({"appart_id": appart_id, "group_id" : str(ObjectId()), "name" : group_name, "owner_id": user_id, "position": pos, "nb_place" : nb_place - 1, "members" : in_group})
        return json.dumps({
            "status": "success",
            "message": "Group created successfully"
        }, indent=2, default=json_util.default), 201
    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong"
        }, indent=2, default=json_util.default), 400

@SERVICES_REQUEST.route('/appart/group/join', methods=['POST'])
def join():
    try:
        #token verif
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400
        d_token = decode_auth_token(auth_token)
        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        data = request.get_json()
        if not data :
            return json.dumps({
            "status": "error",
            "message": "No data sent" 
        }, indent=2, default=json_util.default), 400
        user_id = d_token[1]
        group_id = data["group_id"]
        #check if user in group
 
        test = None
        all_groups = GROUPS.find()
        for i in all_groups:
            if user_id in i["members"]:
                test = user_id
        if test :
            return json.dumps({
            "status": "error",
            "message": "User already in group, please delete your group or leave a group"
        }, indent=2, default=json_util.default), 400

        members = GROUPS.find_one({"group_id": group_id})["members"]
        nb_place = GROUPS.find_one({"group_id": group_id})["nb_place"]
        members.append(user_id)
        GROUPS.find_one_and_update({"group_id":group_id}, {"$set": {"members": members, "nb_place": nb_place - 1}})
        return json.dumps({
            "status": "sucess",
            "message": "joined the group successfully"
        }, indent=2, default=json_util.default), 201

    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong"
        }, indent=2, default=json_util.default), 400

@SERVICES_REQUEST.route('/appart/groups/my', methods=['GET'])
def my_groups():
    try:
        #token verif
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400
        d_token = decode_auth_token(auth_token)
        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        user_id = d_token[1]
        #check if user in group

        to_return = []
        result = GROUPS.find()

        for i in result:
            if (user_id in i["members"]):
                del i["_id"]
                del i["group_id"]
                to_return.append(i)
        

        return json.dumps({
            "status": "success",
            "message": to_return
        }, indent=2, default=json_util.default), 200
        

    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong"
        }, indent=2, default=json_util.default), 400

@SERVICES_REQUEST.route('/groups/for/appart', methods=['GET'])
def groups_by_appart():
    try:
        #token verif
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400
        d_token = decode_auth_token(auth_token)
        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400
        #check if user in group
        args = request.args
        data = args.to_dict()
        to_return = []
        result = GROUPS.find({"appart_id": data["appart_id"]})

        for i in result:
            del i["_id"]
            to_return.append(i)
        

        return json.dumps({
            "status": "success",
            "message": to_return
        }, indent=2, default=json_util.default), 200
        

    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong"
        }, indent=2, default=json_util.default), 400

@SERVICES_REQUEST.route('/appart/group/leave', methods=['POST'])
def leave():
    try:
        #token verif
        auth_token = get_auth_token()
        if not auth_token:
            return json.dumps({"status": "error", "message": "Please provide a valid token"}, indent = 2),400
        d_token = decode_auth_token(auth_token)
        if not d_token[0]:
            return json.dumps({"status": "error", "message": d_token[1]}, indent = 2),400

        data = request.get_json()
        if not data :
            return json.dumps({
            "status": "error",
            "message": "No data sent" 
        }, indent=2, default=json_util.default), 400
        user_id = d_token[1]
        group_id = data["group_id"]
        #check if user in group

        members = GROUPS.find_one({"group_id": group_id})["members"]
        nb_place = GROUPS.find_one({"group_id": group_id})["nb_place"]
        owner_id = GROUPS.find_one({"group_id": group_id})["owner_id"]
        members.remove(user_id)

        if owner_id == user_id and len(members) != 0:
            GROUPS.find_one_and_update({"group_id":group_id}, {"$set": {"owner_id": members[0], "members": members, "nb_place": nb_place + 1}})
        if len(members) == 0:
            GROUPS.delete_one({"group_id": group_id})
        return json.dumps({
            "status": "sucess",
            "message": "left the group successfully"
        }, indent=2, default=json_util.default), 201

    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong"
        }, indent=2, default=json_util.default), 400