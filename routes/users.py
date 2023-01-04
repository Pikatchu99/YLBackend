"""The Endpoints to manage the BOOK_REQUESTS"""
from .required_packages import (Blueprint, request,  json, get_auth_token)
from .required_packages import decode_auth_token
from .required_packages import USERS

USERS_ = Blueprint('user', __name__)

@USERS_.route('/details', methods=['GET'])
def all():
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
        if "user_id" not in data:
            data["user_id"]

        my_request = USERS.find_one({"user_id": data["user_id"], "role": "locataire"})
        if not my_request:
            return json.dumps({"status": "error", "message": "User not found"}, indent = 2),404

        if "_id" in my_request:
            del my_request["_id"]
        if "password" in my_request:
            del my_request["password"]

        return json.dumps({"status": "success", "message": "get user detail", "user": my_request}, indent = 2, default=str), 201

    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2),400