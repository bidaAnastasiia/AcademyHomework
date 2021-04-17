import hashlib
from datetime import date, timedelta
from fastapi import FastAPI, Request, Response, status
from pydantic import BaseModel

app = FastAPI()


@app.get("/")
async def read_root():
    return {'message': 'Hello world!'}


@app.get("/method", status_code=200)
async def show_methodGet(request: Request):
    return {"method": request.method}


@app.post("/method", status_code=201)
async def show_methodPost(request: Request):
    return {"method": request.method}


@app.put("/method", status_code=200)
async def show_methodPut(request: Request):
    return {"method": request.method}


@app.delete("/method", status_code=200)
async def show_methodDel(request: Request):
    return {"method": request.method}


@app.options("/method", status_code=200)
async def show_methodOpt(request: Request):
    return {"method": request.method}

@app.get("/auth", status_code=status.HTTP_401_UNAUTHORIZED)
async def auth_method(password: str = "", password_hash: str = ""):
    statusCode = status.HTTP_401_UNAUTHORIZED
    if password_hash == hashlib.sha512(password.encode('utf-8')).hexdigest():
        statusCode = status.HTTP_204_NO_CONTENT
    if not password or not password_hash:
        statusCode = status.HTTP_401_UNAUTHORIZED
    return Response(status_code=statusCode)


class User(BaseModel):
    name: str
    surname: str


i = 0


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_method(user: User):
    global i
    i += 1
    print(user.name + user.surname)
    return {"id": i, "name": user.name, "surname": user.surname,
            "register_date": date.today().strftime("%Y-%m-%d"),
            "vaccination_date": date.today()+timedelta(len(user.name + user.surname))}