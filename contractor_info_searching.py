
def find_contractor_by_name(mongo, name):
    query = {'Thông tin chung.Tên nhà thầu': {'$regex': name, '$options': 'i'}}
    contractor = mongo.db.contractorInformation.find_one(query)
    return contractor
