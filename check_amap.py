import os
import requests
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("AMAP_API_KEY")

def test_amap():
    print(f"使用的 Key: {key[:5]}...{key[-5:] if key else ''}")
    # 尝试最简单的天气查询
    url = "https://restapi.amap.com/v3/weather/weatherInfo"
    params = {"key": key, "city": "110000"} # 北京的 adcode
    
    try:
        response = requests.get(url, params=params)
        print(f"状态码: {response.status_code}")
        print(f"响应内容: {response.text}")
    except Exception as e:
        print(f"请求发生异常: {e}")

if __name__ == "__main__":
    test_amap()
