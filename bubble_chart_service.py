import logging
from app import mongo
from constants import PROVINCES
from price_parser import Price

biddingInvitationsCollection = mongo.db.contractorBiddingInvitations


def gen_chart_for_selection_plans(key_word):
    print(f"Start bubble chart service with {key_word}")

    raw_results = []
    if key_word is not None and key_word != "":
        query = {'Thông tin chi tiết.Tên gói thầu': {'$regex': key_word, '$options': 'i'}}
        raw_results = biddingInvitationsCollection.find(query)
    else:
        raw_results = biddingInvitationsCollection.find()

    max_x = 0  # count
    max_y = 0  # cost

    data = []
    provinces_data = {}

    for result in raw_results:
        try:
            address = result.get("Tham dự thầu", {}).get("Địa điểm thực hiện gói thầu", "")
            province = get_province(address)

            if province != "":
                prev_count = provinces_data.get(province, {}).get("count", 0)
                prev_cost = provinces_data.get(province, {}).get("cost", 0)
                prev_bid = provinces_data.get(province, {}).get("details", [])
                current_bid_name = result.get("Thông tin chi tiết", {}).get("Tên gói thầu", "")
                current_cost = get_price_from_plain_text(result.get("Mở thầu", {}).get("Dự toán gói thầu", ""))

                prev_bid.append({"Tên gói thầu": current_bid_name, "Giá gói thầu": current_cost})

                provinces_data[province] = {"count": prev_count + 1, "cost": current_cost + prev_cost, "details": prev_bid}
                max_x = max(max_x, prev_count + 1)
                max_y = max(max_y, current_cost + prev_cost)

        except:
            logging.info(f"Error when parse {result}")

    domain = {"x": [0, max_x], "y": [0, max_y]}

    for province in provinces_data:
        temp = {
            "province": province,
            "x": provinces_data.get(province, {}).get("count", 0),
            "y": provinces_data.get(province, {}).get("cost", 0),
            "details": provinces_data.get(province, {}).get("details", [])
        }
        data.append(temp)

    return {"domain": domain, "data": data}


def get_province(address):
    not_found = "Not found province of address"

    if address is None or address == "":
        logging.info(not_found)
        return ""

    for province in PROVINCES:
        if province in address:
            return province

    logging.info(not_found)
    return ""


def get_price_from_plain_text(text):
    #  text sample: "1.446.773.846 VND (Một tỷ bốn trăm bốn mươi sáu triệu bảy trăm bảy mươi ba nghìn tám trăm bốn mươi sáu đồng chẵn)"
    if text is None or text == "":
        return 0
    return int(Price.fromstring(text).amount)
