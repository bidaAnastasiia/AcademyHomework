import hashlib
from datetime import date, timedelta
from fastapi import FastAPI, Request, Response, status, Depends, HTTPException, Cookie
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import PlainTextResponse

app = FastAPI()
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()
app.secret_key = "dfhbsrjke463gjgbhfr43yhygf76jkn"
app.access_tokens = ""

@app.get("/")
async def read_root():
    return {'message': 'Hello world!'}


@app.get("/hello")
def hello_html(request: Request):
    return templates.TemplateResponse("index.html.j2", {
        "request": request, "today_date": date.today()})


@app.post("/login_session", status_code=201)
def login(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "4dm1n" or credentials.password != "NotSoSecurePa$$":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        session_token = hashlib.sha256(f"{credentials.username}{credentials.password}{app.secret_key}".encode()).hexdigest()
        app.access_tokens = session_token
        response.set_cookie(key="session_token", value=session_token)


@app.post("/login_token", status_code=201)
def login(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "4dm1n" or credentials.password != "NotSoSecurePa$$":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        token_value = "token value"
        return {"token": token_value}


@app.get("/welcome_session")
def welcome(*, request: Request, session_token: str = Cookie(None), format: str = ""):
    if session_token != app.access_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        if format == "json":
            return {"message": "Welcome!"}
        elif format == "html":
            return templates.TemplateResponse("welcome.html.j2", {"request": request})
        else:
            return PlainTextResponse("Welcome!")


@app.get("/welcome_token")
def welcome(*,request: Request, token: str = "default", format: str = ""):
    if token != app.access_tokens:
        raise  HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        if format == "json":
            return {"message": "Welcome!"}
        elif format == "html":
            return templates.TemplateResponse("welcome.html.j2", {"request": request})
        else:
            return PlainTextResponse("Welcome!")



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
patient_list = []


@app.post("/register", status_code=status.HTTP_201_CREATED)
async def register_method(user: User):
    global i
    i += 1
    bufname = ''.join(symbol for symbol in user.name if symbol.isalpha())
    bufsurname = ''.join(symbol for symbol in user.surname if symbol.isalpha())
    print(bufname + bufsurname)
    delta = timedelta(len(bufname + bufsurname))
    patient = {"id": i, "name": user.name, "surname": user.surname,
               "register_date": date.today().strftime("%Y-%m-%d"),
               "vaccination_date": date.today() + delta}
    global patient_list
    patient_list.append(patient)
    return patient


@app.get("/patient/{id}")
async def get_patient(id: int):
    if id < 1:
        return Response(status_code=status.HTTP_400_BAD_REQUEST)
    global patient_list
    if id > len(patient_list):
        return Response(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return patient_list[id-1]
