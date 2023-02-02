from pandas import DataFrame


BASE_URLS = {"https://api1.com", "https://api2.com", "https://api3.com"}
# this is the URL protocol to access the following APIs
PARAMS = "/?member_id={member_id}"

def fake_request_function(url) -> dict:
    try:
        return(API_RESPONSES.loc[url].to_dict())
    except:
        print(f"no data in API_RESPONSES for {url}")
        raise

API_RESPONSES = DataFrame({"https://api1.com/?member_id=1":
        {"deductible": 1000, "stop_loss": 10000, "oop_max": 5000},
    "https://api2.com/?member_id=1":
        {"deductible": 1200, "stop_loss": 13000, "oop_max": 6000},
    "https://api3.com/?member_id=1":
        {"deductible": 1000, "stop_loss": 10000, "oop_max": 6000}}).T

