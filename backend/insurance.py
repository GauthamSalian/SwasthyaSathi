from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
from dotenv import load_dotenv
import os
from azure.cosmos import CosmosClient
import pandas as pd
load_dotenv()

router = APIRouter()

class InsuranceRequest(BaseModel):
    age: int
    gender: str
    marital_status: str
    pregnancy_status: Optional[str]
    no_of_family: int
    dependents_allowed: Optional[str]
    occupation_type: str
    annual_income: float
    ration_card: Optional[str]
    state: str
    district: str
    health_conditions: Optional[List[str]]
    disability: Optional[str]
    pregnancy_needs: Optional[str]
    language: str
    literacy_level: Optional[str]
    digital_literacy: Optional[str]

class InsuranceResponse(BaseModel):
    suggested_plans: List[dict]

endpoint = os.getenv("AZURE_COSMOS_ENDPOINT")
key = os.getenv("AZURE_COSMOS_KEY")
client = CosmosClient(endpoint, key)
database = client.get_database_client("SwasthyaSathiDB")
container= database.get_container_client("InsurancePlan")

@router.post("/get_insurance_suggestions", response_model=InsuranceResponse)
async def get_insurance_suggestions(request: InsuranceRequest):
    # Step 1: Fetch all plans
    items = list(container.read_all_items())

    # Step 2: Filter using if conditions
    filtered = []
    for plan in items:
        if int(plan["min_age"]) > request.age:
            continue
        if "max_age" in plan and plan["max_age"] and int(plan["max_age"]) < request.age:
            continue
        if plan["gender_eligibility"].lower() not in ["all", request.gender.lower()]:
            continue
        if plan["marital_status_required"].lower() not in ["optional", request.marital_status.lower()]:
            continue
        if plan["pregnancy_required"].lower() not in ["optional", (request.pregnancy_status or "").lower()]:
            continue
        if plan["pregnancy_covered"].lower() not in ["optional", (request.pregnancy_needs or "").lower()]:
            continue
        if int(plan["no_of_family_max"]) < request.no_of_family:
            continue
        if plan["dependents_allowed"].lower() not in ["yes", "optional", (request.dependents_allowed or "").lower()]:
            continue
        if plan["occupation_type"].lower() not in ["all", request.occupation_type.lower()]:
            continue
        if plan["ration_card_required"].lower() == "yes" and not request.ration_card:
            continue
        if not (
            plan["state_coverage"].lower() == "all india" or
            request.state.lower() in plan["state_coverage"].lower()
        ):
            continue
        # Health conditions
        covered = [c.strip().lower() for c in plan["health_conditions_covered"].split(",")]
        if not any(cond.lower() in covered for cond in request.health_conditions or []):
            continue

        # Add matched plan
        filtered.append({
            "scheme_name": plan["scheme_name"],
            "base_sum_insured_range": plan["base_sum_insured_range"],
            "premium_start": plan["premium_start"],
            "claim_process_notes": plan["claim_process_notes"],
            "tags": plan["tags"]
        })

    return InsuranceResponse(suggested_plans=filtered)


"""
Sample Request Body:
{
  "age": 32,
  "gender": "female",
  "marital_status": "married",
  "pregnancy_status": "yes",
  "pregnancy_needs": "yes",
  "no_of_family": 4,
  "dependents_allowed": "yes",
  "occupation_type": "agriculture",
  "annual_income": 180000,
  "ration_card": "yes",
  "state": "Karnataka",
  "district": "Udupi",
  "health_conditions": ["diabetes", "hypertension"],
  "disability": "no",
  "language": "kannada",
  "literacy_level": "basic",
  "digital_literacy": "low"
}
"""