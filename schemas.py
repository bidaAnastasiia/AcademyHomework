from pydantic import BaseModel, PositiveInt, constr


class Supplier(BaseModel):
    SupplierID: PositiveInt = None
    CompanyName: constr(max_length=40)
    ContactName: constr(max_length=30) = None
    ContactTitle: constr(max_length=30) = None
    Address: constr(max_length=60) = None
    City: constr(max_length=15) = None
    Region: constr(max_length=15) = None
    PostalCode: constr(max_length=10) = None
    Country: constr(max_length=15) = None
    Phone: constr(max_length=24) = None
    Fax: constr(max_length=24) = None
    HomePage: constr() = None

    class Config:
        orm_mode = True


class Shipper(BaseModel):
    ShipperID: PositiveInt
    CompanyName: constr(max_length=40)
    Phone: constr(max_length=24)

    class Config:
        orm_mode = True

