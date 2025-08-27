from fastapi import APIRouter
import os
from dotenv import load_dotenv
import requests
from pydantic import BaseModel
load_dotenv()

router = APIRouter()

#defining the formats for request and response bodies
class LocationInput(BaseModel):
    lat: float
    lon: float

class Hospitals(BaseModel):
    list_of_hospitals:list

@router.post("/nearby_hospitals", response_model=Hospitals)
async def get_nearby_hospitals(Location: LocationInput):
    url = "https://atlas.microsoft.com/search/poi/json"
    params = {
        "subscription-key": os.getenv("AZURE_MAPS_SUBSCRIPTION_KEY"),
        "query": "hospital",
        "lat": Location.lat,
        "lon": Location.lon,
        "radius": 15000,
        "api-version": "1.0"
    }
    response = requests.get(url, params=params)
    data = response.json()
    print(data)

    hospitals = [
        {
            "name": item["poi"]["name"],
            "address": item["address"]["freeformAddress"],
            "position": item["position"]
        } for item in data.get("results", [])
    ]

    return Hospitals(
        list_of_hospitals=hospitals
    )
    