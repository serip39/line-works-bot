import json
import jwt as pyjwt
import requests
import urllib
from datetime import datetime, timedelta
from logging import getLogger, StreamHandler

logger = getLogger(__name__)
#ログレベルを設定
logger.setLevel(20)
#ログをコンソール出力するための設定
sh = StreamHandler()
logger.addHandler(sh)

# グローバル変数
DOMAIN_ID = ""
API_ID = ""
SERVER_API_CONSUMER_KEY = ""
SERVER_LIST_ID = ""
SERVER_LIST_PRIVATEKEY = ""
BOT_NO = ""
LINE_ID = ""

def create_jwt():
    iat = int(datetime.now().timestamp())
    exp = int((datetime.now() + timedelta(minutes=30)).timestamp())
    secret = SERVER_LIST_PRIVATEKEY

    json_claim_set = {
        "iss": SERVER_LIST_ID,
        "iat": iat,
        "exp": exp
    }
    json_header = {"alg": "RS256", "typ": "JWT"}

    jwt = pyjwt.encode(json_claim_set, secret, algorithm="RS256", headers=json_header)

    logger.info({
        "action": "create jwt",
        "status": "success",
        "message": "JWT:" + jwt
    })
    return jwt


def get_server_token(jwt):
    url = 'https://auth.worksmobile.com/b/' + API_ID + '/server/token'
    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded; charset=UTF-8'
    }
    form_data = {
        "grant_type" : urllib.parse.quote("urn:ietf:params:oauth:grant-type:jwt-bearer"),
        "assertion" : jwt
    }

    try:
        response = requests.post(url=url, headers=headers, data=form_data)
        access_token = json.loads(response.text)["access_token"]
        logger.info({
            "action": "get access token",
            "status": "success",
            "message": "access_token:" + access_token
        })
        return access_token
    except:
        logger.info({
            "action": "get access token",
            "status": "fail",
            "message": response.text
        })
        return response

def api(url, payload, access_token):
    headers = {
        'Content-Type' : 'application/json; charset=UTF-8',
        'consumerKey': SERVER_API_CONSUMER_KEY,
        'Authorization': 'Bearer ' + access_token,
    }
    try:
        response = requests.post(url=url, headers=headers, data=json.dumps(payload))
        logger.info({
            "action": "api request",
            "status": "success",
            "message": response.text
        })
    except:
        logger.info({
            "action": "api request",
            "status": "fail",
            "message": response.text
        })

def register_domain(access_token):
    url = 'https://apis.worksmobile.com/r/' + API_ID + '/message/v1/bot/' + BOT_NO + '/domain/' + DOMAIN_ID
    payload = {
        "usePublic": True,
        "usePermission": False,
    }
    api(url, payload, access_token)

def send_message(access_token):
    url = 'https://apis.worksmobile.com/r/' + API_ID + '/message/v1/bot/' + BOT_NO + '/message/push'
    payload = {
        "accountId": LINE_ID,
        "content": {
            "type": "text",
            "text": "Hello World",
        }
    }
    api(url, payload, access_token)

if __name__ == "__main__":
    jwt = create_jwt()
    access_token = get_server_token(jwt)
    register_domain(access_token)
    send_message(access_token)
