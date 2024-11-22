import random
from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('')
db = client['MedConnect']

# Collections
providers_collection = db['provider-data']
provider_insurance_collection = db['provider-insurance']

# List of insurance plans
insurance_plans = [
    "Blue Cross Blue Shield",
    "UnitedHealthcare",
    "Aetna",
    "Cigna",
    "Humana",
    "Kaiser Permanente",
    "Molina Healthcare",
    "Centene",
    "Oscar Health"
]

# Define the last processed provider ID
last_provider_id = 1992764021  # Replace with your actual last processed _id

# Fetch providers with _id greater than the last processed ID
providers = providers_collection.find(
    {"_id": {"$gt": last_provider_id}},  # Filter to start from the last processed provider
)

# Randomly assign insurance plans to each provider
try:
    for provider in providers:
        provider_id = provider["_id"]
        
        # Randomly assign 1-4 insurance plans
        assigned_insurances = random.sample(insurance_plans, random.randint(1, 4))
        
        # Create mapping documents for each assigned insurance
        mappings = [
            {"provider_id": provider_id, "insurance_name": insurance}
            for insurance in assigned_insurances
        ]
        
        # Insert mappings into provider-insurances collection
        provider_insurance_collection.insert_many(mappings)
        
        # Print progress
        print(f"Processed provider: {provider_id}")
finally:
    providers.close()  # Ensure the cursor is closed

print("Random insurance mappings added successfully!")