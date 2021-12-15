import logging

from flask import Flask, Response, request
from flask_pymongo import PyMongo
from utils import *
from flask_cors import CORS, cross_origin
from bson.objectid import ObjectId


app = Flask(__name__)
app.config['MONGO_URI'] = 'mongodb+srv://dinhhh:IhMxVdQkr7rrDj4f@dauthau-bk.cqscj.mongodb.net/DauThau-BK?retryWrites=true&w=majority'
app.config['JSON_AS_ASCII'] = False
mongo = PyMongo(app)
cors = CORS(app)


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
            query = {'Thông tin chi tiết.Tên gói thầu': {'$regex': key_word, '$options': 'i'}}
            raw_results = mongo.db.contractorBiddingResults.find(query).skip(page * size).limit(size)

    mapping_result = []
    for result in raw_results:
        try:
            temp = {}
            temp["_id"] = result["_id"]
            temp["Thông tin chi tiết"] = {}
            temp["Thông tin chi tiết"]["Tên gói thầu"] = result["Thông tin chi tiết"]["Tên gói thầu"]
            temp["Thông tin chi tiết"]["Bên mời thầu"] = result["Thông tin chi tiết"]["Bên mời thầu"]
            temp["Ngày đăng tải"] = result["Ngày đăng tải"]
            temp["Kết quả"] = {}
            temp["Kết quả"]["Nhà thầu trúng thầu"] = result["Kết quả"]["Nhà thầu trúng thầu"]
            temp["Kết quả"]["Giá trúng thầu"] = result["Kết quả"]["Giá trúng thầu"]
            mapping_result.append(temp)
        except:
            logging.warning("Error when mapping field with raw result {}".format(result))
    response = convert_to_resp(mapping_result)
    return response


@app.route('/api/contractor-bidding_invitations')
@cross_origin()
def get_contractor_invitations_paging():
    page, size = get_page_and_size(request)
    app.logger.info("Start get investor result with page = {} and size = {}".format(page, size))
    raw_results = mongo.db.contractorBiddingInvitations.find().skip(page * size).limit(size)
    mapping_result = []
    for result in raw_results:
        try:
            temp = {}
            temp["_id"] = result["_id"]
            temp["Thông tin chi tiết"] = {}
            temp["Thông tin chi tiết"]["Tên gói thầu"] = result["Thông tin chi tiết"]["Tên gói thầu"]
            temp["Thông tin chi tiết"]["Bên mời thầu"] = result["Thông tin chi tiết"]["Bên mời thầu"]
            temp["Ngày đăng tải"] = result["Thời điểm đăng tải"]
            temp["Hình thức dự thầu"] = result["Tham dự thầu"]["Hình thức dự thầu"]
            temp["Địa điểm thực hiện gói thầu"] = result["Tham dự thầu"]["Địa điểm thực hiện gói thầu"]
            mapping_result.append(temp)
        except:
            logging.warn("Error when mapping field with raw result {}".format(result))
    response = convert_to_resp(mapping_result)
    return response


@app.route('/api/contractor-selection-plans')
@cross_origin()
def get_contractor_selection_plans_paging():
    page, size = get_page_and_size(request)
    app.logger.info("Start get investor result with page = {} and size = {}".format(page, size))
    raw_results = mongo.db.contractorSelectionPlans.find().skip(page * size).limit(size)
    mapping_result = []
    for result in raw_results:
        try:
            temp = {}
            temp["_id"] = result["_id"]
            temp["Thông tin chi tiết"] = {}
            temp["Thông tin chi tiết"]["Tên KHLCNT"] = result["Thông tin chi tiết"]["Tên KHLCNT"]
            temp["Thông tin chi tiết"]["Bên mời thầu"] = result["Thông tin chi tiết"]["Bên mời thầu"]
            temp["Thông tin chi tiết"]["Phân loại"] = result["Thông tin chi tiết"]["Phân loại"]
            temp["Ngày đăng tải"] = result["Ngày đăng tải"]
            temp["Giá dự toán"] = result["Thông tin chi tiết"]["Giá dự toán"]
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
    document = mongo.db.contractorHistory.find({"Tên nhà thầu": contractor_name})
    response = convert_to_resp(document)
    return response


@app.route('/api/search-goods-by-name/<good_name>')
@cross_origin()
def search_goods_by_name(good_name):
    page, size = get_page_and_size(request)
    name = good_name.lower()
    app.logger.info("Start search goods by name = {}".format(name))
    query = {'Mô tả tóm tắt gói thầu.Tên hàng hóa': {'$regex': name, '$options': 'i'}}
    raw_results = mongo.db.contractorBiddingResults.find(query).skip(page * size).limit(size)

    mapping_result = []
    for result in raw_results:
        try:
            temp = {}
            temp["_id"] = result["_id"]
            temp["Tên gói thầu"] = result["Thông tin chi tiết"]["Tên gói thầu"]
            temp["Bên mời thầu"] = result["Thông tin chi tiết"]["Bên mời thầu"]
            temp["Nhà thầu trúng thầu"] = result["Kết quả"]["Nhà thầu trúng thầu"]
            temp["Hàng hóa"] = []
            index = 1
            if result["Mô tả tóm tắt gói thầu"] is not None:
                for good in result["Mô tả tóm tắt gói thầu"]:
                    if name in good["Tên hàng hóa"].lower():
                        goodd = good
                        goodd["STT"] = str(index)
                        index += 1
                        temp["Hàng hóa"].append(goodd)

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
        request_body = request.get_json()
        key_word = request_body.get("keyword", '')
        app.logger.info("Keyword = {}".format(key_word))

        query_for_general_info = {'Thông tin chung.Tên nhà thầu': {'$regex': key_word, '$options': 'i'}}
        general_info = mongo.db.contractorInformation.find(query_for_general_info)

        query_for_history_info = {'Tên nhà thầu': {'$regex': key_word, '$options': 'i'}}
        history_info = mongo.db.contractorHistory.find(query_for_history_info)

        mapping_result = []
        contractor_name_set = []

        for contractor in general_info:
            try:
                temp = {}
                temp["_id"] = contractor["_id"]
                temp["Tên nhà thầu"] = contractor["Thông tin chung"]["Tên nhà thầu"]
                temp["Số ĐKKD"] = contractor["Thông tin chung"]["Số ĐKKD"]
                temp["Phân loại doanh nghiệp"] = contractor["Thông tin chung"]["Phân loại doanh nghiệp"]

                if temp["Tên nhà thầu"] not in contractor_name_set:
                    contractor_name_set.append(temp["Tên nhà thầu"])
                    mapping_result.append(temp)
            except:
                app.logger.warning("Mapping fail in general info")

        for contractor in history_info:
            try:
                temp = {}
                temp["_id"] = contractor["_id"]
                temp["Tên nhà thầu"] = contractor["Tên nhà thầu"]
                temp["Số ĐKKD"] = ''
                temp["Phân loại doanh nghiệp"] = ''

                if temp["Tên nhà thầu"] not in contractor_name_set:
                    contractor_name_set.append(temp["Tên nhà thầu"])
                    mapping_result.append(temp)
            except:
                app.logger.warning("Mapping fail in history {}".format(contractor))

        app.logger.info("Mapping result before filter {}".format(len(mapping_result)))
        return convert_to_resp(mapping_result)

    return {}


@app.route('/api/search-contractor-info-by-obj-id/<object_id>')
@cross_origin()
def get_contractor_by_obj_id(object_id):
    app.logger.info("Start search contractor with object id {}".format(object_id))
    results = mongo.db.contractorInformation.find({"_id": ObjectId(object_id)})
    response = convert_to_resp_with_out_prefix(results[0])
    return response


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
