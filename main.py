from fastapi import FastAPI, Request

app = FastAPI()


@app.get("/")
async def read_root():
    return {'message': 'Hello world!'}

@app.get("/method")
async def show_method(request: Request):
    print(request.method)
    return {"method": request.method}
