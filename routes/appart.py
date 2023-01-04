from .required_packages import (Blueprint, request, json, APPARTEMENTS)
from bson import json_util

APPART_REQUEST = Blueprint('appart', __name__)


@APPART_REQUEST.route('/details', methods=['GET'])
def details():
    try:
        args = request.args
        data = args.to_dict()

        to_return = APPARTEMENTS.find_one({"appart_id": data["appart_id"]})

        return json.dumps({
            "status": "success",
            "message": "search appart",
            "data": to_return,
        }, indent=2, default=json_util.default), 200

    except Exception as e:
        print(e)
        return json.dumps({
            "status": "error",
            "message": "Something went wrong"
        }, indent=2, default=json_util.default), 400
