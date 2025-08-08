import json
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests

app = FastAPI()
templates = Jinja2Templates(directory="templates")

API_KEY = "YOUR_API_KEY"
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

# ✅ Cache only city names (small memory footprint)
cities_cache = None

def get_cities():
    global cities_cache
    if cities_cache is None:  # load once
        with open("city.list.json", encoding="utf-8") as f:
            data = json.load(f)
            cities_cache = [c["name"] for c in data]
    return cities_cache

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/weather", response_class=HTMLResponse)
async def fetch_weather(request: Request):
    form = await request.form()
    city = form["city"]

    params = {
        "q": city,
        "appid": API_KEY,
        "units": "metric"
    }

    response = requests.get(BASE_URL, params=params)

    if response.status_code != 200:
        weather = {"error": response.json().get("message", "Unknown error")}
    else:
        data = response.json()
        weather = {
            "city": data["name"],
            "temperature": data["main"]["temp"],
            "description": data["weather"][0]["description"],
            "humidity": data["main"]["humidity"],
            "wind_speed": data["wind"]["speed"]
        }

    cities = ["Delhi", "Mumbai", "Chennai", "Bengaluru", "Hyderabad", "Kolkata"]
    return templates.TemplateResponse("index.html", {
        "request": request,
        "cities": cities,
        "selected_city": city,
        "weather": weather
    })

@app.get("/search")
def search_cities(q: str = Query(..., min_length=3)):
    matches = [
        name for name in get_cities()
        if name.lower().startswith(q.lower())
    ]
    return {"results": matches[:100]}
