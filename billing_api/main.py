from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import schemas
from typing import List
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

MONGODB_URL = os.getenv("MONGODB_URL")
if not MONGODB_URL:
    raise RuntimeError("MONGODB_URL is not set in the .env file")

client = MongoClient(MONGODB_URL)
# Get default database defined in the connection string
db = client.get_default_database()

# Unified billing collection instead of separate subscriptions and payments
billing_collection = db["billing"]

"""
API Gateway Explanation:
The API Gateway serves as the single entry point for all client requests.
Instead of clients communicating directly with this Subscription & Billing service on port 5004,
they make requests to the API Gateway (e.g., on port 8080).
The API Gateway then routes the relevant requests (like /billing) to this 
microservice internally. It handles cross-cutting concerns like authentication, rate limiting, and 
CORS, keeping this microservice focused purely on its core domain logic without exposing it directly.
"""

app = FastAPI(title="Subscription & Billing Service", docs_url="/docs")

def serialize_doc(doc) -> dict:
    if not doc:
        return None
    # Convert MongoDB ObjectId to string
    doc["id"] = str(doc.pop("_id"))
    return doc

@app.post("/billing", response_model=schemas.BillingResponse)
def create_billing(billing: schemas.BillingCreate):
    # Check if user already has a billing record
    existing_billing = billing_collection.find_one({"user_id": billing.user_id})
    if existing_billing:
        raise HTTPException(status_code=400, detail="Billing record already exists for this user. Use PUT to update.")

    new_billing = {
        "user_id": billing.user_id,
        "subscription_type": billing.subscription_type,
        "price": billing.price,
        "card_number": billing.card_number,
        "status": "Active",
        "created_at": datetime.utcnow()
    }
    result = billing_collection.insert_one(new_billing)
    inserted_billing = billing_collection.find_one({"_id": result.inserted_id})
    return serialize_doc(inserted_billing)

@app.get("/billing/{user_id}", response_model=schemas.BillingResponse)
def get_billing(user_id: int):
    billing_record = billing_collection.find_one({"user_id": user_id})
    if billing_record is None:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return serialize_doc(billing_record)

@app.put("/billing/{user_id}", response_model=schemas.BillingResponse)
def update_billing(user_id: int, billing_update: schemas.BillingUpdate):
    existing_billing = billing_collection.find_one({"user_id": user_id})
    if not existing_billing:
        raise HTTPException(status_code=404, detail="Billing record not found")

    # Extract only the fields that were provided in the request
    update_data = billing_update.dict(exclude_unset=True)
    
    if update_data:
        billing_collection.update_one(
            {"_id": existing_billing["_id"]},
            {"$set": update_data}
        )
    
    updated_billing = billing_collection.find_one({"_id": existing_billing["_id"]})
    return serialize_doc(updated_billing)

@app.delete("/billing/{user_id}")
def delete_billing(user_id: int):
    result = billing_collection.delete_one({"user_id": user_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Billing record not found")
    return {"message": "Billing record deleted successfully"}
