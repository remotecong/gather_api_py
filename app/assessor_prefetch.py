""" script to prefetch all assessor datas! """
from mongo import add_phone_data, find_docs_like
from owner_parsers.tulsa import fetch_owner_data_from_permalink

if __name__ == "__main__":
    counter = 0
    for doc in find_docs_like({"assessorAccountNumber": {"$exists": True}, "ownerName": None}):
        if not doc.get("assessorAccountNumber"):
            continue
        url = "https://www.assessor.tulsacounty.org/assessor-property.php" + \
            "?account={}&go=1".format(doc.get("assessorAccountNumber"))
        print("\nAssessor Lookup with Permalink: {} --- ".format(url))
        try:
            assessor_data = fetch_owner_data_from_permalink(url)
            if assessor_data:
                updates = {
                    "ownerName": assessor_data.get("owner_name"),
                    "ownerLivesThere": assessor_data.get("lives_there"),
                }
                house_num = assessor_data.get("assessor_house_number")
                if house_num and doc["address"].find(house_num) != 0:
                    updates["houseNumConflict"] = house_num
                    print("Found a conflict for {}\n{} !== {}\n".format(doc["_id"], house_num, doc["address"]))
                add_phone_data(doc, updates)
                counter = counter + 1
        except Exception as e:
            print("xxxxxxxxxxx bad dates\n{}\n{}\n{}\n{}\n".format(doc["address"], doc["_id"], doc["assessorAccountNumber"], e))
    print("Okay! Done here. Worked on {} locations! Whew!".format(counter))
