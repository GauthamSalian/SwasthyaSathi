from dotenv import load_dotenv
import os
from azure.cosmos import CosmosClient
import csv
load_dotenv()

endpoint = os.getenv("AZURE_COSMOS_ENDPOINT")
key = os.getenv("AZURE_COSMOS_KEY")
client = CosmosClient(endpoint, key)
database = client.get_database_client("SwasthyaSathiDB")
container = database.get_container_client("InsurancePlan")

def clean_text(text):
    if not text:
        return ""
    return (
        text.replace("â‚¹", "₹")
            .replace("â„¢", "™")
            .replace("â€“", "–")
            .replace("â€”", "—")
            .replace("â€˜", "‘")
            .replace("â€™", "’")
            .replace("â€œ", "“")
            .replace("â€", "”")
            .replace("Â", "")  # Removes stray encoding artifacts
            .strip()
    )

with open("schemes.csv", "r") as file:
    reader = csv.DictReader(file)
    for row in reader:
        doc = {
            "id": row["plan_id"],
            "scheme_name": clean_text(row["scheme_name"]),
            "uin": row["uin"],
            "min_age": row["min_age"],
            "max_age": row["max_age"],
            "gender_eligibility": row["gender_eligibility"],
            "marital_status_required": row["marital_status_required"],
            "pregnancy_required": row["pregnancy_required"],
            "pregnancy_covered": row["pregnancy_covered"],
            "no_of_family_max": row["no_of_family_max"],
            "dependents_allowed": row["dependents_allowed"],
            "occupation_type": row["occupation_type"],
            "income_limit": row["income_limit"],
            "ration_card_required": row["ration_card_required"],
            "state_coverage": row["state_coverage"],
            "district_restriction": row["district_restriction"],
            "health_conditions_covered": row["health_conditions_covered"],
            "disability_required": row["disability_required"],
            "literal_level_required": row["literacy_level_required"],
            "digital_literacy_required": row["digital_literacy_required"],
            "language_support": row["language_support"],
            "base_sum_insured_range": clean_text(row["base_sum_insured_range"]),
            "premium_start": clean_text(row["premium_start"]),
            "claim_process_notes": clean_text(row["claim_process_notes"]),
            "mental_health_support": row["mental_health_support"],
            "home_treatment": row["home_treatment"],
            "HLTH_meter_available": row["HLTH_meter_available"],
            "HealthReturns_available":row["HealthReturns_available"],
            "SuperCredit_available": row["SuperCredit_available"],
            "ClaimProtect_available": row["ClaimProtect_available"],
            "cashless_network_size": row["cashless_network_size"],
            "tags": row["tags"]
        }
        container.create_item(body=doc)