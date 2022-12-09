import requests
import json


with open("config.json") as f:
    CONFIG = json.load(f)

BASE_URL = "https://api.youneedabudget.com/v1"

def session():
    session = requests.Session()
    token = CONFIG["token"]
    session.headers = {"Authorization": f"Bearer {token}"}
    return session