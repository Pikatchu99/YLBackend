"""The Endpoints to manage the BOOK_REQUESTS"""
from .required_packages import (Blueprint, request, jsonify, ObjectId, json, _key, get_auth_token, datetime)
from .required_packages import decode_auth_token, get_user_info, datetime
from .required_packages import (ToCiDi)
from bson import json_util

TCD = Blueprint('tcd', __name__)

@TCD.route('/all', methods=['GET'])
def get_all_country():
    try:
        all_to_ci_dy = ToCiDi.find_one({})
        data = []
        if '_id' in all_to_ci_dy:
            del all_to_ci_dy['_id']
        data = all_to_ci_dy["country"]

        return json.dumps({"status": "success", "message": "get all country", "country": data, "total": len(data)}, indent = 2), 202
    except KeyError as error:
        return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
    except Exception as error:
        return json.dumps({"status": "error", "message": str(error)}, indent = 2),400

# @TCD.route('/town/all', methods=['GET'])
# def get_all_town():
#     try:
#         all_apparts = APPARTEMENTS.find({})
#         data = []
#         for one_appart in all_apparts:
#             data.append(one_appart["town"].lower())
#         return json.dumps({"status": "success", "message": "get all town", "town": data, "total": len(data)}, indent = 2), 202
#     except KeyError as error:
#         return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
#     except Exception as error:
#         return json.dumps({"status": "error", "message": str(error)}, indent = 2),400

# @TCD.route('/district/all', methods=['GET'])
# def get_all_district():
#     try:
#         all_apparts = APPARTEMENTS.find({})
#         data = []
#         for one_appart in all_apparts:
#             data.append(one_appart["district"].lower())
#         return json.dumps({"status": "success", "message": "get all district", "district": data, "total": len(data)}, indent = 2), 202
#     except KeyError as error:
#         return json.dumps({"status": "error", "message": "key error: " + str(error)}, indent = 2),400
#     except Exception as error:
#         return json.dumps({"status": "error", "message": str(error)}, indent = 2),400