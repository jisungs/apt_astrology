import os
import requests
from dotenv import load_dotenv

load_dotenv()

PUBLIC_API_KEY = os.getenv("PUBLIC_API_KEY")

URL = "http://apis.data.go.kr/1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev"
params = {
    "serviceKey": PUBLIC_API_KEY,
    "pageNo": 1,
    "numOfRows": 1000,
    "LAWD_CD": "11140",
    "DEAL_YMD": "202411",
}
response = requests.get(URL, params=params)
data = response.text
print(data)