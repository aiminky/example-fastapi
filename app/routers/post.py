from .. import models, schemas, oauth2
from fastapi import APIRouter, Depends, FastAPI, Response, status, HTTPException
from sqlalchemy.orm import Session
from ..database import engine, SessionLocal, get_db
from cgi import print_arguments
from fastapi import Depends, FastAPI, Response, status, HTTPException

from sqlalchemy import func
from typing import List, Optional
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from ..database import engine, SessionLocal, get_db


router = APIRouter(
    # prefix="/post" + /id # cái này mặc định các link trong file đêu bắt đầu bằng "/post" để ta có thể bỏ từ "post" trong app.get đi
    tags=['Posts']
) # router thay thế cho app vì đã chuyển khỏi main.py

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


my_posts = [{"title":"title of post 1", "content":"content of post 1", "id": 1},
            {"title":"title of post 2", "content":"content of post 2", "id": 2},
            {"title":"title of post 3", "content":"content of post 3", "id": 3}]

def find_post(id):
    for p in my_posts:
        if p['id'] == id:
            return p
        

def find_index_post(id: int):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

# ORMs - SQL alchemy

@router.get("/sqlalchemy", response_model=List[schemas.Post])
def test_post(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()
    return posts


@router.post("/sqlalchemy", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), 
                current_user : int =  Depends(oauth2.get_current_user)): # user_id: để xác thực người dùng đã login vào rồi mới được dùng post request này
    print(current_user.email) # current_user : int =  Depends(oauth2.get_current_user)
    new_post = models.Post( # nhập data
        # title=post.title, content=post.content, published=post.published
        **post.model_dump())
    db.add(new_post) # add vào database
    db.commit() # để lưu vào database
    db.refresh(new_post) # returning lại post, xem lại kết quả post

    return new_post

@router.get("/sqlalchemy/{id}", response_model=List[schemas.Post])
def get_post(id: int, db: Session = Depends(get_db)):
    posts = db.query(models.Post).filter(models.Post.id == id).first()

    if not posts:    
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post wwith id: {id} was not found")

    return{posts}


@router.delete("/sqlalchemy/{id}", status_code=status.HTTP_204_NO_CONTENT)
def  delete_post(id: int, db: Session = Depends(get_db), 
                ):
    delete_post = db.query(models.Post).filter(models.Post.id == id)

    if delete_post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post wwith id: {id} was not found")

    delete_post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/sqlalchemy/{id}", response_model=schemas.Post)
def put_posts(id = int, update_post = schemas.PostCreate ,db: Session = Depends(get_db),
              ):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post wwith id: {id} was not found")

    post_query.update(update_post.model_dump(), synchronize_session=False)
    db.commit()
    return {post}


# Python + Raw SQL: sử dugnj lệnh SQL để làm việc với pgadmin database

@router.get("/posts")
async def root():
    cursor.execute("""SELECT * from posts; """)
    posts = cursor.fetchall() #fetchall: xem tất cả các data, fetchone: xem 1 data
    return {"data": posts}


@router.post("/posts", status_code=status.HTTP_201_CREATED)
async def createposts(post: schemas.PostCreate):
    cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s);""", (post.title,
                                                                                              post.content, post.published))
    # post.title, post.content, post.published: để lấy title, content, published từ post
    new_post = cursor.fetchone() # add data
    conn.commit() # để lưu vào database

    #post_dict = post.model_dump()
    #post_dict['id'] = randrange(0, 100000000)
    #my_posts.append(post_dict)
    return new_post



@router.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("""SELECT * from posts WHERE id = %s """, (str(id)))
    post = cursor.fetchone()
    
    # Post = find_post(id)
    if not schemas.Post:    
         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post wwith id: {id} was not found")

       # response.status_code = status.HTTP_404_NOT_FOUND
       # return {'post wwith id: {id} was not found'}
    return {"post_detail": post}

@router.get("/posts/latest")
def get_latest_post():
    post = my_posts[len(my_posts)-1]
    return {'detail': post}


@router.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def  delete_post(id: int):
    #deleta post  
    #find the index in the array that has required ID
    #my_post.pop(index)

    cursor.execute("""DELETE FROM posts WHERE id = %s returning *; """, (str(id),))
    delete_post = cursor.fetchone()
    conn.commit()

    # index = find_index_post(id)

    if delete_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post wwith id: {id} was not found")

    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/posts/{id}")
def update_post(id: int, post: schemas.PostCreate):
    cursor.execute("""UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id)))
    update_post = cursor.fetchone()
    conn.commit()
    # index = find_index_post(id)

    if update_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail=f"post wwith id: {id} was not found")
    # post_dict = post.model_dump()
    # post_dict['id'] = id
    # my_posts[update_post] = post_dict
    return {'data': update_post}