from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import pandas as pd

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

@router.post("/get_insurance_suggestions", response_model=InsuranceResponse)
async def get_insurance_suggestions(request: InsuranceRequest):
    # Load CSV
    df = pd.read_csv("schemes.csv")

    # Age filter
    df = df[
        (df["min_age"] <= request.age) &
        ((df["max_age"].isna()) | (df["max_age"] >= request.age))
    ]

    # Gender filter
    df = df[
        (df["gender_eligibility"].str.lower() == request.gender.lower()) |
        (df["gender_eligibility"].str.lower() == "all")
    ]

    # Marital status
    df = df[
        (df["marital_status_required"].str.lower() == request.marital_status.lower()) |
        (df["marital_status_required"].str.lower() == "optional")
    ]

    # Pregnancy filters
    df = df[
        (df["pregnancy_required"].str.lower() == (request.pregnancy_status or "").lower()) |
        (df["pregnancy_required"].str.lower() == "optional")
    ]
    df = df[
        (df["pregnancy_covered"].str.lower() == (request.pregnancy_needs or "").lower()) |
        (df["pregnancy_covered"].str.lower() == "optional")
    ]

    # Family size
    df = df[df["no_of_family_max"] >= request.no_of_family]

    # Dependents
    df = df[
        (df["dependents_allowed"].str.lower() == (request.dependents_allowed or "").lower()) |
        (df["dependents_allowed"].str.lower() == "yes") |
        (df["dependents_allowed"].str.lower() == "optional")
    ]

    # Occupation
    df = df[
        (df["occupation_type"].str.lower() == request.occupation_type.lower()) |
        (df["occupation_type"].str.lower() == "all")
    ]

    # Ration card
    df = df[
        (df["ration_card_required"].str.lower() == "no") |
        (request.ration_card is not None)
    ]

    # State coverage
    df = df[
        (df["state_coverage"].str.lower() == "all india") |
        (df["state_coverage"].str.contains(request.state, case=False, na=False))
    ]

    # Health conditions
    df["covered_conditions"] = df["health_conditions_covered"].str.lower().str.split(",")
    df = df[
        df["covered_conditions"].apply(
            lambda conds: any(c.lower() in conds for c in request.health_conditions or [])
        )
    ]

    # Final output
    final_df = df[[
        "scheme_name",
        "base_sum_insured_range",
        "premium_start",
        "claim_process_notes",
        "tags"
    ]].to_dict(orient="records")

    return InsuranceResponse(suggested_plans=final_df)
