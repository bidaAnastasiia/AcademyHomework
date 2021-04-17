from fastapi import FastAPI, Request, status, Response

app = FastAPI()


@app.get("/")
async def read_root():
    return {'message': 'Hello world!'}


@app.get("/method")
async def show_method(request: Request, response:Response):
    if request.method == 'POST':
        response.status_code = status.HTTP_201_CREATED
    return {"method": request.method}
