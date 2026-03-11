from fastapi import FastAPI,HTTPException,Depends
from sqlalchemy import create_engine,Column,Integer,Float,String
from sqlalchemy.orm import declarative_base,Session,sessionmaker
from pydantic import BaseModel
from typing import Optional,List

app = FastAPI(title="Integration with SQL - Code with Josh")

@app.get("/")
def root():
    return {
        "message": "Intro to fastAPI with sql"
    }