import hashlib
from datetime import date, timedelta

import uvicorn
from fastapi import FastAPI, Request, Response, status, Depends, HTTPException, Cookie
from pydantic import BaseModel
from fastapi.templating import Jinja2Templates
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from starlette.responses import PlainTextResponse, RedirectResponse
import random
import string
import sqlite3

app = FastAPI()
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()
app.secret_key = "dfhbsrjke463gjgbhfr43yhygf76jkn"
app.access_tokens = []
app.token_values = []

class Category(BaseModel):
    name: str


@app.on_event("startup")
async def startup():
    app.db_connection = sqlite3.connect("northwind.db")
    app.db_connection.text_factory = lambda b: b.decode(errors="ignore")  # northwind specific


@app.on_event("shutdown")
async def shutdown():
    app.db_connection.close()


@app.get("/")
async def read_root():
    return {'message': 'Hello world!'}


@app.get("/categories")
async def categories():
    categories = app.db_connection.execute(
        "SELECT CategoryID, CategoryName FROM Categories ORDER BY CategoryID").fetchall()
    categories = [{"id": category[0], "name": category[1]} for category in categories]
    return {
        "categories": categories
    }


@app.post("/categories", status_code=201)
async def add_category(category: Category):
    cursor = app.db_connection.execute(
        f"INSERT INTO Categories (CategoryName) VALUES ('{category.name}')"
    )
    app.db_connection.commit()
    print("POST NAME: "+category.name)
    return {
        "id": cursor.lastrowid,
        "name": category.name
    }


@app.put("/categories/{category_id}")
async def update_category(category_id: int, category: Category):
    categorytest = app.db_connection.execute("SELECT * FROM Categories WHERE CategoryID = ?", (category_id,)).fetchone()
    if categorytest is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        cursor = app.db_connection.execute(
            "UPDATE Categories SET CategoryName = ? WHERE CategoryID = ?", (
                category.name, category_id)
        )
        app.db_connection.commit()
        print("PUT NAME: " + category.name)
        return {
            "id": cursor.lastrowid,
            "name": category.name
        }



@app.delete("/categories/{category_id}")
async def delete_category(category_id: int):
    category = app.db_connection.execute("SELECT * FROM Categories WHERE CategoryID = ?", (category_id,)).fetchone()
    if category is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        cursor = app.db_connection.execute(
            "DELETE FROM Categories WHERE CategoryID = ?", (category_id,)
        )
        app.db_connection.commit()
        return {"deleted": cursor.rowcount}




@app.get("/customers")
async def customers():
    customers = app.db_connection. \
        execute("SELECT CustomerID, CompanyName, coalesce(Address,'') || ' ' || coalesce(PostalCode,'') || ' ' "
                "|| coalesce(City,'') || ' ' || coalesce(Country,'') "
                "as full_address FROM Customers ORDER BY CustomerID").fetchall()
    customers = [
        {"id": customer[0], "name": customer[1], "full_address": customer[2]}
        for customer in customers]
    return {
        "customers": customers
    }


@app.get("/products/{product_id}")
async def products(product_id: int):
    product = app.db_connection.execute("SELECT ProductID, ProductName FROM Products WHERE ProductID = ?",
                                        (product_id,)).fetchone()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        return {"id": product[0], "name": product[1]}


@app.get("/products/{product_id}/orders")
async def products(product_id: int):
    product = app.db_connection.execute("SELECT ProductID, ProductName FROM Products WHERE ProductID = ?",
                                        (product_id,)).fetchone()
    if product is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    else:
        orders = app.db_connection.execute("SELECT Products.ProductID, Orders.OrderId,Customers.CompanyName, "
                                           "[Order Details].Quantity, "
                                           "[Order Details].Quantity*[Order Details].UnitPrice-"
                                           "([Order Details].Discount*[Order Details].Quantity"
                                           "*[Order Details].UnitPrice)as total_price "
                                           "FROM [Order Details] JOIN Orders ON Orders.OrderID "
                                           "= [Order Details].OrderID JOIN Products ON Products.ProductID "
                                           "= [Order Details].ProductID JOIN Customers ON Customers.CustomerID "
                                           "= Orders.CustomerID WHERE Products.ProductID = ? ORDER BY Orders.OrderId",
                                           (product_id, )).fetchall()

        orders = [{"id": order[1], "customer":order[2], "quantity": round(order[3], 2), "total_price":round(order[4], 2)}
                  for order in orders]
        return {"orders": orders}


@app.get("/employees")
async def employees(order: str = "EmployeeID", limit: int = -1, offset: int = 0):
    if order not in ["EmployeeID", "first_name", "last_name", "city"]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    employees = app.db_connection.execute(
        "SELECT EmployeeID,LastName as last_name,FirstName as first_name,City FROM Employees ORDER BY " + order + " LIMIT ? OFFSET ?",
        (limit, offset)).fetchall()

    employees = [{"id": employee[0], "last_name": employee[1], "first_name": employee[2], "city": employee[3]}
                 for employee in employees]
    return {"employees": employees}


@app.get("/products_extended")
async def products_extended():
    products = app.db_connection.execute("SELECT Products.ProductID, Products.ProductName, Categories.CategoryName,"
                                         "Suppliers.CompanyName FROM Products JOIN Categories ON Products.CategoryID "
                                         "= Categories.CategoryID JOIN Suppliers ON Products.SupplierID "
                                         "= Suppliers.SupplierID ").fetchall()
    products = [{"id": product[0], "name": product[1], "category": product[2], "supplier": product[3]} for product in
                products]
    return {"products_extended":products}


@app.get("/hello")
def hello_html(request: Request):
    return templates.TemplateResponse("index.html.j2", {
        "request": request, "today_date": date.today()})


@app.post("/login_session", status_code=201)
def login(response: Response, credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "4dm1n" or credentials.password != "NotSoSecurePa$$":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        letters = string.ascii_lowercase
        secret_key = ''.join(random.choice(letters) for i in range(10))
        session_token = hashlib.sha256(f"{credentials.username}{credentials.password}{secret_key}".encode()).hexdigest()
        if len(app.access_tokens) == 3:
            app.access_tokens = app.access_tokens[1:]
        app.access_tokens.append(session_token)
        print("GENERATE SESSION: " + session_token)
        response.set_cookie(key="session_token", value=session_token)


@app.post("/login_token", status_code=201)
def login(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "4dm1n" or credentials.password != "NotSoSecurePa$$":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        letters = string.ascii_lowercase
        token_value = ''.join(random.choice(letters) for i in range(10))
        if len(app.token_values) == 3:
            app.token_values = app.token_values[1:]
        app.token_values.append(token_value)
        print("GENERATE TOKEN: " + token_value)
        return {"token": token_value}


@app.get("/welcome_session")
def welcome(*, request: Request, session_token: str = Cookie(None), format: str = ""):
    if session_token not in app.access_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        if format == "json":
            return {"message": "Welcome!"}
        elif format == "html":
            return templates.TemplateResponse("welcome.html.j2", {"request": request})
        else:
            return PlainTextResponse("Welcome!")


@app.get("/welcome_token")
def welcome(*, request: Request, token: str = "default", format: str = ""):
    if token not in app.token_values:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        if format == "json":
            return {"message": "Welcome!"}
        elif format == "html":
            return templates.TemplateResponse("welcome.html.j2", {"request": request})
        else:
            return PlainTextResponse("Welcome!")


@app.delete("/logout_session")
def delete_session(session_token: str = Cookie(None), format: str = ""):
    if session_token not in app.access_tokens:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        app.access_tokens.remove(session_token)
        response = RedirectResponse(url='/logged_out?format=' + format, status_code=status.HTTP_302_FOUND)
        return response


@app.delete("/logout_token")
def delete_token(token: str = "default", format: str = ""):
    if token not in app.token_values:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        app.token_values.remove(token)
        response = RedirectResponse(url='/logged_out?format=' + format, status_code=status.HTTP_302_FOUND)
        return response


@app.get("/logged_out")
def logged_out(request: Request, format: str = ""):
    if format == "json":
        return {"message": "Logged out!"}
    elif format == "html":
        return templates.TemplateResponse("l_out.html.j2", {"request": request})
    else:
        return PlainTextResponse("Logged out!")


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
        return patient_list[id - 1]



# if __name__ == "__main__":
#     uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
