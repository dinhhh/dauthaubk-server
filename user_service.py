import logging

from flask_bcrypt import Bcrypt
from app import mongo
from constants import COLLECTION_CONSTANTS

LINH_VUC = "Lĩnh vực"

CATEGORY = "bidCategory"

HINH_THUC_THAU = "Hình thức đấu thầu"

DIA_PHUONG = "Địa phương"

LOAI_THONG_TIN = "Loại thông tin"

BEN_MOI_THAU = "Bên mời thầu"

NHA_THAU = "Nhà thầu"

BID_CATEGORY = "bidCategory"

BID_FORM = "bidForm"

PROVINCE = "province"

INFO_CATEGORY = "infoCategory"

SOLICITOR = "solicitor"

FAIL_MESSAGE = "Fail"


MESSAGE = "message"

SUCCESS_MESSAGE = "Success"

user_collection = mongo.db.users
user_sub_bid = mongo.db.usersSubscribeBidding
contractor_bidding_results = mongo.db.contractorBiddingResults
bcrypt = Bcrypt()


def register(username, password, email, account_type):
    messages = {}

    if account_type not in (NHA_THAU, "Nhà đầu tư"):
        messages[MESSAGE] = "Account type is not valid"
        return messages

    if not (isinstance(username, str) and isinstance(password, str) and isinstance(email, str)):
        messages[MESSAGE] = "User name, password, email must be string"
        return messages

    e_user = user_collection.find_one({'email': email})
    if e_user is not None:
        messages[MESSAGE] = "Account already exist. Please try another"
        return messages

    new_user = {
        "username": username,
        "password": bcrypt.generate_password_hash(password).decode("utf-8"),
        "email": email,
        "Tài khoản": account_type
    }
    user_collection.insert_one(new_user)
    messages[MESSAGE] = SUCCESS_MESSAGE
    return messages


def login(email, password):
    e_user = user_collection.find_one({'email': email})
    if e_user is not None:
        if bcrypt.check_password_hash(e_user['password'], password):
            return {MESSAGE: SUCCESS_MESSAGE}
    return {MESSAGE: FAIL_MESSAGE}


def subscribe(email, sub_info):
    messages = {}
    e_user = user_collection.find_one({'email': email})
    if e_user is None:
        messages[MESSAGE] = "User not found"
        return messages

    if not isinstance(sub_info, dict):
        messages[MESSAGE] = "Invalid parameter"
        return messages

    categories = sub_info.get(INFO_CATEGORY, "").split(", ")
    for category in categories:
        user_collection.update_one({"email": email},
                                   {"$set": {f"{category}.{BEN_MOI_THAU}": sub_info[SOLICITOR],
                                             f"{category}.{DIA_PHUONG}": sub_info[PROVINCE],
                                             f"{category}.{HINH_THUC_THAU}": sub_info[BID_FORM],
                                             f"{category}.{LINH_VUC}": sub_info[BID_CATEGORY]}},
                                   upsert=True)
    messages[MESSAGE] = SUCCESS_MESSAGE
    return messages


def broadcast(collection_name, item):
    collection_info = {}
    for constant in COLLECTION_CONSTANTS:
        if constant["collection_name"] == collection_name:
            collection_info = constant
            break

    if not collection_info:
        raise Exception("Collection info not found")

    users = user_collection.find()
    logging.info("Find all users")
    subscribers = []
    for user in users:
        sub_info = user[collection_info["name"]]
        if sub_info is not None:
            if (is_empty_or_none(sub_info["Bên mời thầu"]) or (sub_info["Bên mời thầu"] != "" and sub_info["Bên mời thầu"] in get_solicitor_in_item(item))) and \
                    (is_empty_or_none(sub_info["Hình thức đấu thầu"]) or (sub_info["Hình thức đấu thầu"] in item["Hình thức đấu thầu"])) and \
                    (is_empty_or_none(sub_info["Lĩnh vực"]) or (sub_info["Lĩnh vực"] in item.get("Lĩnh vực", ""))):
                # TODO: Kiểm tra địa phương?
                subscribers.append(user)

    print(f"Subscribers: {subscribers}")
    for subscriber in subscribers:
        update = {"$addToSet": {f"{collection_info['name']}": item}}
        user_sub_bid.update_one({"email": subscriber["email"]},
                                {"$addToSet": {f"{collection_info['name']}": item}},
                                upsert=True)
    return {MESSAGE: SUCCESS_MESSAGE}


def get_all_subs(email):
    return user_sub_bid.find_one({"email": email})

def get_solicitor_in_item(item):
    return item.get("Thông tin chi tiết", {}).get("Bên mời thầu", "")


def is_empty_or_none(field):
    return field == "" or field is None

