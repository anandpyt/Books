from fastapi import FastAPI, Request,Query
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os, requests
from dotenv import load_dotenv
import json
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()
app = FastAPI()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org/data/2.5/weather"

templates = Jinja2Templates(directory="templates")

def load_cities():
    with open("city.list.json", encoding="utf-8") as f:
        for city in json.load(f):
            yield city["name"]
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})
# Handle form POST
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
    matches = []
    for name in load_cities():
        if name.lower().startswith(q.lower()):
            matches.append(name)
            if len(matches) >= 100:  # limit results
                break
    return {"results": matches}
