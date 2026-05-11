from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
import sqlalchemy
from src.api import auth
from src import database as db

router = APIRouter(
    prefix="/plans",
    tags=["plans"],
    dependencies=[Depends(auth.get_api_key)],
)