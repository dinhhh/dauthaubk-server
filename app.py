import logging

from flask import Flask, Response, request, jsonify
from flask_pymongo import PyMongo
from flask_swagger_ui import get_swaggerui_blueprint

import contractor_info_searching
import user_service

from utils import *
from flask_cors import CORS, cross_origin
from bson.objectid import ObjectId

from datetime import timedelta
from flask_jwt_extended import create_access_token
from flask_jwt_extended import create_refresh_token
from flask_jwt_extended import get_jwt_identity
from flask_jwt_extended import jwt_required
from flask_jwt_extended import JWTManager


app = Flask(__name__)
app.config['MONGO_URI'] = "Your DB path here"
app.config['JSON_AS_ASCII'] = False
app.config["JWT_SECRET_KEY"] = "super-secret" # TODO: Change later
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=100000)
app.config["JWT_REFRESH_TOKEN_EXPIRES"] = timedelta(days=30)

### swagger specific ###
SWAGGER_URL = '/swagger'
API_URL = '/static/swagger.json'
SWAGGERUI_BLUEPRINT = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': "Swagger UI"
    }
)
### end swagger specific ###
app.register_blueprint(SWAGGERUI_BLUEPRINT, url_prefix=SWAGGER_URL)


mongo = PyMongo(app)
cors = CORS(app)
jwt = JWTManager(app)

import bubble_chart_service
import bidding_search_service

investorInfoCollection = mongo.db.investorInformation
investorSelectCollection = mongo.db.investorSelectionResults
contractorBidResultCollection = mongo.db.contractorBiddingResults
contractorBidInviteCollection = mongo.db.contractorBiddingInvitations


@app.route('/api/investor-info')
def get_investor_info():
    investors = mongo.db.investorInformation.find()
    response = convert_to_resp(data=investors)
    return response


@app.route('/api/investor-selection-results')
def get_investor_results_paging():
    page, size = get_page_and_size(request)
    app.logger.info("Start get investor result with page = {} and size = {}".format(page, size))
    results = mongo.db.investorSelectionResults.find().skip(page * size).limit(size)
    response = convert_to_resp(results)
    return response


@app.route('/api/contractor-selection-results', methods=['GET', 'POST'])
@cross_origin()
def get_contractor_results_paging():
    page, size = get_page_and_size(request)
    app.logger.info("Start get investor result with page = {} and size = {}".format(page, size))

    raw_results = []
    if request.method == 'GET':
        raw_results = mongo.db.contractorBiddingResults.find().skip(page * size).limit(size)

    if request.method == 'POST':
        app.logger.info("Get contractor selection result with post method")
        request_body = request.get_json()
        key_word = request_body.get("keyword", '')
        app.logger.info("Keyword = {}".format(key_word))
        if key_word != '':
            query = {'Th??ng tin chi ti???t.T??n g??i th???u': {'$regex': key_word, '$options': 'i'}}
            raw_results = mongo.db.contractorBiddingResults.find(query).skip(page * size).limit(size)

    mapping_result = []
    for result in raw_results:
        try:
            temp = {}
            temp["_id"] = result["_id"]
            temp["Th??ng tin chi ti???t"] = {}
            temp["Th??ng tin chi ti???t"]["T??n g??i th???u"] = result["Th??ng tin chi ti???t"]["T??n g??i th???u"]
            temp["Th??ng tin chi ti???t"]["B??n m???i th???u"] = result["Th??ng tin chi ti???t"]["B??n m???i th???u"]
            temp["Ng??y ????ng t???i"] = result["Ng??y ????ng t???i"]
            temp["K???t qu???"] = {}
            temp["K???t qu???"]["Nh?? th???u tr??ng th???u"] = result["K???t qu???"]["Nh?? th???u tr??ng th???u"]
            temp["K???t qu???"]["Gi?? tr??ng th???u"] = result["K???t qu???"]["Gi?? tr??ng th???u"]
            mapping_result.append(temp)
        except:
            logging.warning("Error when mapping field with raw result {}".format(result))
    response = convert_to_resp(mapping_result)
    return response


@app.route('/api/contractor-bidding_invitations', methods=['GET', 'POST'])
@cross_origin()
def get_contractor_invitations_paging():
    page, size = get_page_and_size(request)
    app.logger.info("Start get investor result with page = {} and size = {}".format(page, size))

    bidding_invitations_collection = mongo.db.contractorBiddingInvitations
    raw_results = []
    if request.method == 'GET':
        raw_results = bidding_invitations_collection.find().skip(page * size).limit(size)
    if request.method == 'POST':
        key_word = request.get_json().get("keyword", '')
        app.logger.info(f"Search bidding invitations with keyword {key_word}")
        query = {}
        if key_word != "" and key_word is not None:
            query = {'Th??ng tin chi ti???t.T??n g??i th???u': {'$regex': key_word, '$options': 'i'}}
        raw_results = bidding_invitations_collection.find(query).skip(page * size).limit(size)

    mapping_result = []
    for result in raw_results:
        try:
            temp = {}
            temp["_id"] = result["_id"]
            temp["Th??ng tin chi ti???t"] = {}
            temp["Th??ng tin chi ti???t"]["T??n g??i th???u"] = result["Th??ng tin chi ti???t"]["T??n g??i th???u"]
            temp["Th??ng tin chi ti???t"]["B??n m???i th???u"] = result["Th??ng tin chi ti???t"]["B??n m???i th???u"]
            temp["Ng??y ????ng t???i"] = result["Th???i ??i???m ????ng t???i"]
            temp["H??nh th???c d??? th???u"] = result["Tham d??? th???u"]["H??nh th???c d??? th???u"]
            temp["?????a ??i???m th???c hi???n g??i th???u"] = result["Tham d??? th???u"]["?????a ??i???m th???c hi???n g??i th???u"]
            mapping_result.append(temp)
        except:
            logging.warn("Error when mapping field with raw result {}".format(result))
    response = convert_to_resp(mapping_result)
    return response


@app.route('/api/contractor-selection-plans', methods=['POST', 'GET'])
@cross_origin()
def get_contractor_selection_plans_paging():
    page, size = get_page_and_size(request)
    app.logger.info("Start get investor result with page = {} and size = {}".format(page, size))

    selectionPlanCollection = mongo.db.contractorSelectionPlans
    raw_results = []
    if request.method == 'GET':
        raw_results = selectionPlanCollection.find().skip(page * size).limit(size)

    if request.method == 'POST':
        key_word = request.get_json().get("keyword", '')
        app.logger.info(f"Search selection plans with keyword {key_word}")
        query = {}
        if key_word != "" and key_word is not None:
            query = {'Th??ng tin chi ti???t.T??n KHLCNT': {'$regex': key_word, '$options': 'i'}}
        raw_results = selectionPlanCollection.find(query).skip(page * size).limit(size)

    mapping_result = []
    for result in raw_results:
        try:
            temp = {}
            temp["_id"] = result["_id"]
            temp["Th??ng tin chi ti???t"] = {}
            temp["Th??ng tin chi ti???t"]["T??n KHLCNT"] = result["Th??ng tin chi ti???t"]["T??n KHLCNT"]
            temp["Th??ng tin chi ti???t"]["B??n m???i th???u"] = result["Th??ng tin chi ti???t"]["B??n m???i th???u"]
            temp["Th??ng tin chi ti???t"]["Ph??n lo???i"] = result["Th??ng tin chi ti???t"]["Ph??n lo???i"]
            temp["Ng??y ????ng t???i"] = result["Ng??y ????ng t???i"]
            temp["Gi?? d??? to??n"] = result["Th??ng tin chi ti???t"]["Gi?? d??? to??n"]
            mapping_result.append(temp)
        except:
            logging.warning("Error when mapping field with raw result {}".format(result))
    response = convert_to_resp(mapping_result)
    return response


@app.route('/api/contractor-selection-results/<object_id>')
@cross_origin()
def get_contractor_results_by_object_id(object_id):
    app.logger.info("Start get contractor result with object id = {}".format(object_id))
    results = mongo.db.contractorBiddingResults.find({"_id": ObjectId(object_id)})
    response = convert_to_resp(results)
    return response


@app.route('/api/contractor-history/<contractor_name>')
@cross_origin()
def get_contractor_history_by_name(contractor_name):
    app.logger.info("Start get contractor history with name = {}".format(contractor_name))
    document = mongo.db.contractorHistory.find({"T??n nh?? th???u": contractor_name})
    response = convert_to_resp(document)
    return response


@app.route('/api/search-goods-by-name/<good_name>')
@cross_origin()
def search_goods_by_name(good_name):
    page, size = get_page_and_size(request)
    name = good_name.lower()
    app.logger.info("Start search goods by name = {}".format(name))
    query = {'M?? t??? t??m t???t g??i th???u.T??n h??ng h??a': {'$regex': name, '$options': 'i'}}
    raw_results = mongo.db.contractorBiddingResults.find(query).skip(page * size).limit(size)

    mapping_result = []
    for result in raw_results:
        try:
            temp = {}
            temp["_id"] = result["_id"]
            temp["T??n g??i th???u"] = result["Th??ng tin chi ti???t"]["T??n g??i th???u"]
            temp["B??n m???i th???u"] = result["Th??ng tin chi ti???t"]["B??n m???i th???u"]
            temp["Nh?? th???u tr??ng th???u"] = result["K???t qu???"]["Nh?? th???u tr??ng th???u"]
            temp["H??ng h??a"] = []
            index = 1
            if result["M?? t??? t??m t???t g??i th???u"] is not None:
                for good in result["M?? t??? t??m t???t g??i th???u"]:
                    if name in good["T??n h??ng h??a"].lower():
                        goodd = good
                        goodd["STT"] = str(index)
                        index += 1
                        temp["H??ng h??a"].append(goodd)

            mapping_result.append(temp)
        except:
            logging.warning("Error when mapping field with raw result {}".format(result))

    response = convert_to_resp(mapping_result)
    return response


@app.route('/api/search-contractor-info', methods=['POST'])
@cross_origin()
def search_contractor_info():
    if request.method == 'POST':
        app.logger.info("Get contractor selection result with post method")
        page, size = get_page_and_size(request)
        request_body = request.get_json()
        key_word = request_body.get("keyword", '')
        app.logger.info("Keyword = {}".format(key_word))

        query_for_general_info = {'Th??ng tin chung.T??n nh?? th???u': {'$regex': key_word, '$options': 'i'}}
        general_info = mongo.db.contractorInformation.find(query_for_general_info).skip(page * size).limit(size)

        query_for_history_info = {'T??n nh?? th???u': {'$regex': key_word, '$options': 'i'}}
        history_info = mongo.db.contractorHistory.find(query_for_history_info).skip(page * size).limit(size)

        mapping_result = []
        contractor_name_set = []

        for contractor in general_info:
            try:
                temp = {}
                temp["_id"] = contractor["_id"]
                temp["T??n nh?? th???u"] = contractor["Th??ng tin chung"]["T??n nh?? th???u"]
                temp["S??? ??KKD"] = contractor["Th??ng tin chung"]["S??? ??KKD"]
                temp["Ph??n lo???i doanh nghi???p"] = contractor["Th??ng tin chung"]["Ph??n lo???i doanh nghi???p"]

                if temp["T??n nh?? th???u"] not in contractor_name_set:
                    contractor_name_set.append(temp["T??n nh?? th???u"])
                    mapping_result.append(temp)
            except:
                app.logger.warning("Mapping fail in general info")

        for contractor in history_info:
            try:
                temp = {}
                temp["_id"] = contractor["_id"]
                temp["T??n nh?? th???u"] = contractor["T??n nh?? th???u"]
                temp["S??? ??KKD"] = ''
                temp["Ph??n lo???i doanh nghi???p"] = ''

                if temp["T??n nh?? th???u"] not in contractor_name_set:
                    contractor_name_set.append(temp["T??n nh?? th???u"])
                    mapping_result.append(temp)
            except:
                app.logger.warning("Mapping fail in history {}".format(contractor))

        app.logger.info("Mapping result before filter {}".format(len(mapping_result)))
        return convert_to_resp(mapping_result)

    return {}

@app.route('/api/search-contractor-by-name/<name>')
@cross_origin()
def get_contractor_by_name(name):
    app.logger.info("Get contractor by name {}".format(name))
    return convert_to_resp(contractor_info_searching.find_contractor_by_name(mongo=mongo, name=name))

@app.route('/api/search-contractor-info-by-obj-id/<object_id>')
@cross_origin()
def get_contractor_by_obj_id(object_id):
    # object id = 61ac2619238b0f5027bb122a -> history collection
    # object id = 61ac245a238b0f5027ba8502 -> contractor information collection
    app.logger.info("Start search contractor with object id {}".format(object_id))
    result = {}
    general_info = list(mongo.db.contractorInformation.find({"_id": ObjectId(object_id)}).limit(1))
    history_info = list(mongo.db.contractorHistory.find({"_id": ObjectId(object_id)}).limit(1))

    app.logger.info("general_info {}".format(list(general_info)))
    app.logger.info("history_info {}".format(list(history_info)))
    app.logger.info(len(list(general_info)))
    app.logger.info(len(list(history_info)))

    if len(list(general_info)) > 0 and len(list(history_info)) > 0:
        raise Exception("Duplicate obj id")

    if len(general_info) > 0:
        info = general_info[0]
        app.logger.info(info["Th??ng tin chung"] )
        result["Th??ng tin chung"] = info["Th??ng tin chung"]
        result["Th??ng tin ng??nh ngh???"] = info["Th??ng tin ng??nh ngh???"]

        name = info["Th??ng tin chung"]["T??n nh?? th???u"]
        history = list(mongo.db.contractorHistory.find({"T??n nh?? th???u": name}).limit(1))
        if len(history) > 0:
            result["G??i th???u ???? tham gia"] = history[0]["G??i th???u ???? tham gia"]
        else:
            result["G??i th???u ???? tham gia"] = []

    if len(history_info) > 0:
        app.logger.info("History info > 0")
        history = history_info[0]
        name = history["T??n nh?? th???u"]
        result["G??i th???u ???? tham gia"] = history["G??i th???u ???? tham gia"]

        general = list(mongo.db.contractorHistory.find({"Th??ng tin chung.T??n nh?? th???u": name}).limit(1))
        if len(general) > 0:
            result["Th??ng tin chung"] = general[0]["Th??ng tin chung"]
            result["Th??ng tin ng??nh ngh???"] = general[0]["Th??ng tin ng??nh ngh???"]
        else:
            result["Th??ng tin chung"] = {}
            result["Th??ng tin chung"]["T??n nh?? th???u"] = history["T??n nh?? th???u"]
            result["Th??ng tin ng??nh ngh???"] = []

    response = convert_to_resp_with_out_prefix(result)
    return response


@app.route("/api/user/register", methods=['POST'])
@cross_origin()
def register():
    app.logger.info("User api register")
    username = request.json['username']
    pw = request.json['password']
    email = request.json['email']
    account_type = request.json['type']
    messages = user_service.register(username=username, password=pw, email=email, account_type=account_type)
    if messages[user_service.MESSAGE] != user_service.SUCCESS_MESSAGE:
        return jsonify(messages), 422
    else:
        return jsonify(messages), 200


@app.route("/api/user/login", methods=['POST'])
@cross_origin()
def login():
    app.logger.info("User api login")
    pw = request.json['password']
    email = request.json['email']
    messages = user_service.login(email=email, password=pw)
    if messages[user_service.MESSAGE] != user_service.SUCCESS_MESSAGE:
        return jsonify(messages), 422
    else:
        # TODO: usage example: https://flask-jwt-extended.readthedocs.io/en/stable/basic_usage/
        access_token = create_access_token(identity=email)
        refresh_token = create_refresh_token(identity=email)
        return jsonify(access_token=access_token, refresh_token=refresh_token), 200


@app.route("/api/user/refresh", methods=['POST'])
@cross_origin()
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    access_token = create_access_token(identity=identity)
    return jsonify(access_token=access_token)


@app.route("/api/user/subscribe", methods=['POST'])
@cross_origin()
@jwt_required()
def subscribe():
    current_user = get_jwt_identity()
    app.logger.info(f"User {current_user} subscribe")
    sub_info = {
        user_service.SOLICITOR: request.json.get("solicitor", ""),
        user_service.INFO_CATEGORY: request.json["infoCategory"],
        user_service.PROVINCE: request.json["province"],
        user_service.BID_CATEGORY: request.json["bidCategory"],
        user_service.BID_FORM: request.json["bidForm"]
    }
    messages = user_service.subscribe(current_user, sub_info)
    if messages[user_service.MESSAGE] != user_service.SUCCESS_MESSAGE:
        return jsonify(messages), 422
    else:
        return jsonify(messages), 200


@app.route("/api/user/broadcast", methods=['POST'])
@cross_origin()
def broadcast():
    app.logger.info(f"Broadcast with request body {request.json}")
    user_service.broadcast(request.json["collection"], request.json["item"])
    return jsonify({"message": "success"}), 200


@app.route("/api/user/get-subs", methods=['POST'])
@cross_origin()
@jwt_required()
def get_subs():
    current_user = get_jwt_identity()
    app.logger.info(f"Current user: {current_user}")
    bids = convert_to_resp_with_out_prefix(user_service.get_all_subs(current_user))
    return bids, 200


@app.route("/api/bubble-chart/bidding-invitation", methods=['POST'])
@cross_origin()
def gen_bubble_chart_for_selection_plans():
    key_word = request.json.get("keyword", "")
    app.logger.info(f"Start gen bubble chart for bidding invitation with {key_word}")
    return bubble_chart_service.gen_chart_for_selection_plans(key_word), 200


@app.route("/api/search-bid-by-name", methods=['POST'])
@cross_origin()
def search_bid_by_name():
    bid_name = request.json.get("bidName", "")
    solicitor = request.json.get("solicitor", "")
    is_plan = request.json.get("isPlan", False)
    app.logger.info(f"Search bid by name {bid_name} and solicitor {solicitor}")
    return convert_to_resp_with_out_prefix(bidding_search_service.search_by_bid_name_and_solicitor(bid_name,
                                                                                                   solicitor,
                                                                                                   is_plan)), 200
    # {
    #     "bidName": "Mua s???m sinh ph???m x??t nghi???m nhanh kh??ng nguy??n vi r??t SARS-Cov-2 ph???c v??? c??ng t??c ph??ng ch???ng d???ch Covid-19 c???a B???nh vi???n ??KKV B???ng S??n n??m 2021 (?????t 2)",
    #     "solicitor": "B???nh Vi???n ??a Khoa Khu V???c B???ng S??n",
    #     "isPlan": false
    # }


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
