from fastapi import FastAPI, Request, status, Response

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