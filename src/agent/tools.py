import os
import requests
from typing import List, Dict, Any, Optional
from agent.models import Attraction, Hotel, WeatherInfo, Location

# 修正：不要在模块级别直接赋值，否则导入时如果环境变量未加载会拿到 None
def get_amap_key():
    return os.getenv("AMAP_API_KEY")

CITY_ADCODE = {
    "北京": "110000",
    "上海": "310000",
    "广州": "440100",
    "深圳": "440300",
    "杭州": "330100",
    "南京": "320100",
    "成都": "510100",
    "西安": "610100"
}

def get_adcode(city_name: str) -> str:
    for name, code in CITY_ADCODE.items():
        if name in city_name:
            return code
    return city_name

def search_amap_poi(keywords: str, city: str, types: str = "") -> List[Dict[str, Any]]:
    formatted_keywords = keywords.replace("，", "|").replace(",", "|")
    url = "https://restapi.amap.com/v3/place/text"
    params = {
        "key": get_amap_key(),
        "keywords": formatted_keywords,
        "city": city,
        "citylimit": "true",
        "types": types,
        "offset": 5,
        "page": 1,
        "output": "JSON"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        if data["status"] == "1" and int(data["count"]) > 0:
            return data["pois"]
        
        if types:
            params.pop("types")
            response = requests.get(url, params=params)
            data = response.json()
            if data["status"] == "1":
                return data["pois"]
        return []
    except Exception as e:
        print(f"高德搜索失败: {e}")
        return []

def get_amap_weather(city: str) -> List[WeatherInfo]:
    adcode = get_adcode(city)
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {
        "key": get_amap_key(),
        "city": adcode,
        "extensions": "all",
        "output": "JSON"
    }
    try:
        response = requests.get(url, params=params)
        data = response.json()
        weather_list = []
        if data["status"] == "1" and "forecasts" in data:
            for f in data["forecasts"]:
                for c in f["casts"][:3]:
                    weather_list.append(WeatherInfo(
                        date=c["date"],
                        day_weather=c["dayweather"],
                        night_weather=c["nightweather"],
                        day_temp=c["daytemp"],
                        night_temp=c["nighttemp"],
                        wind_direction=c["daywind"],
                        wind_power=c["daypower"]
                    ))
                if weather_list: break
        return weather_list
    except Exception as e:
        print(f"天气查询失败: {e}")
        return []

def parse_poi_to_attraction(poi: Dict[str, Any]) -> Attraction:
    lng, lat = poi["location"].split(",")
    return Attraction(
        name=poi["name"],
        address=poi["address"] if isinstance(poi["address"], str) else "未知地址",
        location=Location(longitude=float(lng), latitude=float(lat)),
        visit_duration=120,
        description=poi.get("type", "热门景点"),
        ticket_price=50,
        rating=4.5
    )

def parse_poi_to_hotel(poi: Dict[str, Any]) -> Hotel:
    lng, lat = poi["location"].split(",")
    return Hotel(
        name=poi["name"],
        address=poi["address"] if isinstance(poi["address"], str) else "未知地址",
        location=Location(longitude=float(lng), latitude=float(lat)),
        price_range="300-800",
        rating="4.5",
        estimated_cost=500
    )
