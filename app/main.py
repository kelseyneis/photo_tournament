import requests
import json
import re

from .utilities.users import auth_backend, current_active_user, fastapi_users
from .utilities.vote import Vote
from .database.schemas import UserCreate, UserRead, UserUpdate
from .database.database import User, create_db_and_tables
from .utilities.image import Image
from fastapi import Depends, FastAPI
import uuid
from fastapi.middleware.cors import CORSMiddleware
from uvicorn.middleware.proxy_headers import ProxyHeadersMiddleware
from starlette.responses import FileResponse, RedirectResponse


from fastapi import FastAPI
from fastapi import Depends, FastAPI, Request, Form, Response
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi_users import FastAPIUsers

app = FastAPI()

# set up css and templates
# app.mount("/app/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.add_middleware(ProxyHeadersMiddleware, trusted_hosts="*")


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# Start routers for fastapi-users
app.include_router(
    fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"]
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_verify_router(UserRead),
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get("/authenticated-route")
async def authenticated_route(user: User = Depends(current_active_user)):
    return {"message": f"Hello {user.email}!"}
# End routers for fastapi-users

# Create user tables and get the list of images on startup


@app.on_event("startup")
async def on_startup():
    await create_db_and_tables()
    await Image.get_images()


@app.get("/create_account")
def create_account_page(request: Request):
    return templates.TemplateResponse("create_account.html", {"request": request})


@app.post("/create_account")
def create(request: Request, username: str = Form(None), password: str = Form(None)):
    url = "http://127.0.0.1:8000/auth/register"

    payload = json.dumps({
        "email": username,
        "password": password
    })
    headers = {
        'Content-Type': 'application/json'
    }

    response = requests.request("POST", url, headers=headers, data=payload)
    # TODO: add error handling
    return templates.TemplateResponse("create_account.html", {"request": request, "success": True})


@app.get("/login_user")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/login_user")
def login_user(request: Request, username: str = Form(None), password: str = Form(None)):

    url = "http://127.0.0.1:8000/auth/jwt/login"

    payload = f'username={username}&password={password}'
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }

    response = requests.request("POST", url, headers=headers, data=payload)

    print(response.text)

    # TODO: add error handling
    return templates.TemplateResponse("login.html", {"request": request})


def get_img_id(url):
    x = re.search(r"\d+", url)
    return (x.group())

# TODO: get user and read user file to determine next pair of images to select for each round, following procedure implemented in tourney.py


@app.get("/vote")
def vote_page(request: Request):
    # get image urls (pulled from API at app startup)
    images = open("images.txt", "r").read()
    images_arr = images.split("\n")
    # base url is url without image id
    base_url = re.sub("\d+.*", "", images_arr[0])
    # get image id from url
    img1 = get_img_id(images_arr[0])
    img2 = get_img_id(images_arr[1])
    return templates.TemplateResponse("vote.html", {"request": request, "img1": img1, "img2": img2, "base_url": base_url})


# called when user clicks on one of the images to vote for it
@app.get("/vote/{img}")
# , user: User = Depends(current_active_user)): (Getting Unauthorized response, so proceeding without users)
async def vote(img: str, request: Request):
    # would include user as a parameter to record their vote
    img1, img2 = Vote().vote(img)
    images = open("images.txt", "r").read()
    images_arr = images.split("\n")
    # get url without image id
    base_url = re.sub("\d+.*", "", images_arr[0])
    return templates.TemplateResponse("vote.html", {"request": request, "img1": img1, "img2": img2, "base_url": base_url})
