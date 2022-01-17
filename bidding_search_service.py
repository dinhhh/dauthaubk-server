import logging

from app import mongo
from constants import COLLECTION_CONSTANTS

contractorSelectionPlansCollection = mongo.db.contractorSelectionPlans  # Kế hoạch lựa chọn nhà thầu
contractorPreQualificationResultsCollection = mongo.db.contractorPreQualificationResults  # Kết quả sơ tuyển
contractorBiddingInvitationsCollection = mongo.db.contractorBiddingInvitations  # Thông báo mời thầu
contractorBiddingResultsCollection = mongo.db.contractorBiddingResults  # Kết quả trúng thầu


def search_by_bid_name_and_solicitor(bid_name, solicitor, is_plan):
    if not is_plan:
        result = {}
        bid_result = search_bid_result_by_name(bid_name, solicitor)
        result["Kết quả trúng thầu"] = bid_result
        result["Kế hoạch lựa chọn nhà thầu"] = {}
        result["Kết quả sơ tuyển"] = search_pre_qualification_result(bid_name, solicitor)
        result["Thông báo mời thầu"] = search_bid_invitation(bid_name, solicitor)

        try:
            KHLCNT = bid_result.get("Thông tin chi tiết", {}).get("Số hiệu KHLCNT", "")
            print(f"KHLCNT {KHLCNT}")
            #  KHLCNT.replace(" ", "")
            plan = search_plan_by_KHLCNT(KHLCNT)
            result["Kế hoạch lựa chọn nhà thầu"] = plan
        except:
            print("Not found KHLCNT")

        return result

    else:
        result = {}
        plan = search_plan_by_name(bid_name, solicitor)
        result["Kế hoạch lựa chọn nhà thầu"] = plan
        result["Kết quả trúng thầu"] = None
        result["Kết quả sơ tuyển"] = None
        result["Thông báo mời thầu"] = None
        try:
            KHLCNT = plan.get("Thông tin chi tiết", {}).get("Số KHLCNT", "")
            #  KHLCNT.replace(" ", "")
            bid_result = search_bid_result_by_KHLCNT(KHLCNT)
            result["Kết quả trúng thầu"] = bid_result
            temp_bid_name = bid_result.get("Thông tin chi tiết", {}).get("Tên gói thầu", "")
            result["Kết quả sơ tuyển"] = search_pre_qualification_result(temp_bid_name, solicitor)
            result["Thông báo mời thầu"] = search_bid_invitation(temp_bid_name, solicitor)
        except:
            print("Not found another info by plan no")
        return result

def search_bid_result_by_name(bid_name, solicitor):
    return contractorBiddingResultsCollection.find_one({"$and": [{"Thông tin chi tiết.Tên gói thầu": bid_name},
                                                                 {"Thông tin chi tiết.Bên mời thầu": solicitor}]})


def search_bid_result_by_KHLCNT(KHLCNT):
    return contractorBiddingResultsCollection.find_one({"Thông tin chi tiết.Số hiệu KHLCNT": KHLCNT})


def search_bid_invitation(bid_name, solicitor):
    return contractorBiddingInvitationsCollection.find_one({"$and": [{"Thông tin chi tiết.Tên gói thầu": bid_name},
                                                                     {"Thông tin chi tiết.Bên mời thầu": solicitor}]})


def search_pre_qualification_result(bid_name, solicitor):
    return contractorPreQualificationResultsCollection.find_one({"$and": [{"Thông tin chi tiết.Tên gói thầu": bid_name},
                                                                          {"Thông tin chi tiết.Tên bên mời thầu": solicitor}]})


def search_plan_by_name(name, solicitor):
    return contractorSelectionPlansCollection.find_one({"$and": [{"Thông tin chi tiết.Tên KHLCNT": name},
                                                                 {"Thông tin chi tiết.Bên mời thầu": solicitor}]})


def search_plan_by_KHLCNT(KHLCNT):
    plan = contractorSelectionPlansCollection.find_one({"Thông tin chi tiết.Số KHLCNT": KHLCNT})
    if plan is not None:
        return plan

    for i in range(0, 10):
        condition = KHLCNT + f" - 0{i}"
        print(f"Condition {condition}")
        temp = contractorSelectionPlansCollection.find_one({"Thông tin chi tiết.Số KHLCNT": condition})
        if temp is not None:
            return temp

    return None

# DEMO:
# Kết quả: http://muasamcong.mpi.gov.vn/lua-chon-nha-thau?p_auth=o4FQEogpOu&p_p_id=luachonnhathau_WAR_bidportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=2&_luachonnhathau_WAR_bidportlet_id=345319&_luachonnhathau_WAR_bidportlet_name=8&_luachonnhathau_WAR_bidportlet_javax.portlet.action=detail
# Kế hoạch LCNT: http://muasamcong.mpi.gov.vn/lua-chon-nha-thau?p_auth=o4FQEogpOu&p_p_id=luachonnhathau_WAR_bidportlet&p_p_lifecycle=1&p_p_state=normal&p_p_mode=view&p_p_col_id=column-1&p_p_col_count=2&_luachonnhathau_WAR_bidportlet_id=579374&_luachonnhathau_WAR_bidportlet_name=1&_luachonnhathau_WAR_bidportlet_javax.portlet.action=detail
