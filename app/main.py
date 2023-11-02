from cgi import print_arguments
from fastapi import Depends, FastAPI, Response, status, HTTPException
from fastapi.params import Body
from pydantic import BaseModel

from typing import List, Optional
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from . import models, schemas, utils
from .database import engine, SessionLocal, get_db
from .routers import post, user, auth
from fastapi.middleware.cors import CORSMiddleware



models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# nhập link nào vào đây thì mình có thể dùng api của mình trong trang web đấy ở trong phàn console
# để "*" là web nào cũng dùng được 
origins = ["*"]


app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

while True: # vòng lặp kết nối với database

    try: 
        conn = psycopg2.connect(host = 'localhost', database='fastapi',
                             user='postgres', password='password123', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("succesfull cxfdgfdsg fgdsg")
        break # phá vòng lặp khi thành công ở bước này
    except Exception as error:
        print("failed")
        time.sleep(2) # sau 2 giây chạy lạp vòng lặp khi đến bước này (thất bại)

# class UpdatePost


app.include_router(post.router) # include lấy các @router trong post
app.include_router(user.router)
app.include_router(auth.router)