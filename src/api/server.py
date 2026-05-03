from fastapi import FastAPI
from src.api import admin, users
from starlette.middleware.cors import CORSMiddleware

description = """
Data Fit Meal Tracker is your perfect place for storing meal plans and logging your meals.
"""
tags_metadata = [
    {"name": "admin", "description": "Reset the tracker state."},
    {"name": "user", "description": "Manage User Profiles and Items"}
]

app = FastAPI(
    title="Data Fit Meal Tracker",
    description=description,
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "the Data Fit Team",
        "email": "drmelgoz@calpoly.edu",
    },
    openapi_tags=tags_metadata,
)

origins = ["https://potion-exchange.vercel.app"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)

app.include_router(admin.router)
app.include_router(users.router)



@app.get("/")
async def root():
    return {"message": "Tracker is ready to go!"}
