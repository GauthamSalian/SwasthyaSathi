from azure.cosmos import CosmosClient
from fastapi import APIRouter
from dotenv import load_dotenv
import os
from pydantic import BaseModel
import uuid
import bcrypt
from datetime import datetime
load_dotenv()

router = APIRouter()

endpoint = os.getenv("AZURE_COSMOS_ENDPOINT")
key = os.getenv("AZURE_COSMOS_KEY")

client = CosmosClient(endpoint, key)
database = client.get_database_client("SwasthyaSathiDB")
container = database.get_container_client("Users")

class UserRegistrationRequest(BaseModel):
    username: str
    password: str

class UserLoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    response:str


def check_user_exists(username:str) -> bool:
    query = f"SELECT * FROM Users u WHERE u.username = '{username}'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    return len(items) > 0

@router.post("/register", response_model=UserResponse)
async def register_user(user: UserRegistrationRequest):
    if check_user_exists(user.username):
        return UserResponse(response="Username already exists")
    
    user_id = str(uuid.uuid4())
    username = user.username
    hashed_password = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode("utf-8")
    created_at = datetime.utcnow().isoformat()
    container.create_item(body={
        "id": user_id,
        "username": username,
        "hashed_password": hashed_password,
        "created_at": created_at
    })
    return UserResponse(response="User registered successfully. Login to continue.")

@router.post("/login", response_model=UserResponse)
async def login_user(user: UserLoginRequest):
    query = f"SELECT * FROM Users u WHERE u.username = '{user.username}'"
    items = list(container.query_items(query=query, enable_cross_partition_query=True))
    if len(items) == 0:
        return UserResponse(response="User not found.")
    if bcrypt.checkpw(user.password.encode(), items[0]["hashed_password"].encode()):
        return UserResponse(response="Login successful.")
    else:
        return UserResponse(response="Incorrect Password.")