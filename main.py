from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os, requests, json, gzip
from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

templates = Jinja2Templates(directory="templates")

# ✅ Load compressed city data only once
def load_cities_data():
    with gzip.open("citynames.json.gz", "rt", encoding="utf-8") as f:
        return json.load(f)

cities_data = load_cities_data()  # this now loads from .gz file

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

# @app.get("/search")
# def search_cities(q: str = Query(..., min_length=3)):
#     matches = [
#         city["name"] for city in cities_data
#         if city["name"].lower().startswith(q.lower())
#     ]
#     return {"results": matches[:100]}
@app.get("/search")
def search_cities(q: str = Query(..., min_length=3)):
    if isinstance(cities_data[0], dict):
        # full object JSON
        matches = [
            city["name"] for city in cities_data
            if city["name"].lower().startswith(q.lower())
        ]
    else:
        # already just a list of names
        matches = [
            name for name in cities_data
            if name.lower().startswith(q.lower())
        ]
    return {"results": matches[:100]}