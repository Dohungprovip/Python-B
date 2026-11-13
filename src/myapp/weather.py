import json
import urllib.request

API_URL = "https://api.example.com/weather?city={city}"


def fetch_weather(city):
    with urllib.request.urlopen(API_URL.format(city=city), timeout=5) as resp:
        return json.loads(resp.read().decode("utf-8"))


def describe_weather(city):
    temp = fetch_weather(city)["temp"]
    if temp >= 30:
        return "Nóng"
    if temp >= 20:
        return "Mát mẻ"
    return "Lạnh"
