from bson import ObjectId
from app import mongo


def get_contractor_by_object_id(object_id):
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
        app.logger.info(info["Thông tin chung"])
        result["Thông tin chung"] = info["Thông tin chung"]
        result["Thông tin ngành nghề"] = info["Thông tin ngành nghề"]

        name = info["Thông tin chung"]["Tên nhà thầu"]
        history = list(mongo.db.contractorHistory.find({"Tên nhà thầu": name}).limit(1))
        if len(history) > 0:
            result["Gói thầu đã tham gia"] = history[0]["Gói thầu đã tham gia"]
        else:
            result["Gói thầu đã tham gia"] = []
    if len(history_info) > 0:
        app.logger.info("History info > 0")
        history = history_info[0]
        name = history["Tên nhà thầu"]
        result["Gói thầu đã tham gia"] = history["Gói thầu đã tham gia"]

        general = list(mongo.db.contractorHistory.find({"Thông tin chung.Tên nhà thầu": name}).limit(1))
        if len(general) > 0:
            result["Thông tin chung"] = general[0]["Thông tin chung"]
            result["Thông tin ngành nghề"] = general[0]["Thông tin ngành nghề"]
        else:
            result["Thông tin chung"] = {}
            result["Thông tin chung"]["Tên nhà thầu"] = history["Tên nhà thầu"]
            result["Thông tin ngành nghề"] = []
    return result