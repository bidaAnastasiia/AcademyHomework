from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import PositiveInt
from sqlalchemy.orm import Session
import crud, schemas
import models
from database import get_db

router = APIRouter()


@router.get("/shippers/{shipper_id}", response_model=schemas.Shipper)
async def get_shipper(shipper_id: PositiveInt, db: Session = Depends(get_db)):
    db_shipper = crud.get_shipper(db, shipper_id)
    if db_shipper is None:
        raise HTTPException(status_code=404, detail="Shipper not found")
    return db_shipper


@router.get("/shippers", response_model=List[schemas.Shipper])
async def get_shippers(db: Session = Depends(get_db)):
    return crud.get_shippers(db)


@router.get("/suppliers")
async def get_suppliers(db: Session = Depends(get_db)):
    suppliers = crud.get_suppliers(db)
    suppliers = [{"SupplierID": supplier.SupplierID, "CompanyName": supplier.CompanyName} for supplier in suppliers]
    return suppliers


@router.get("/suppliers/{supplier_id}", response_model=schemas.Supplier)
async def get_shipper(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    return db_supplier


@router.get("/suppliers/{supplier_id}/products")
async def get_products(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    else:
        products = crud.get_products(db, supplier_id)
        products = [{"ProductID": product.ProductID, "ProductName": product.ProductName,
                     "Category":{"CategoryID": product.CategoryID,
                                 "CategoryName": crud.get_product_category(db,product.CategoryID).CategoryName},
                     "Discontinued": product.Discontinued} for product in products]
    return products


@router.post("/suppliers", status_code=201)
async def add_supplier(supplier: schemas.Supplier, db: Session = Depends(get_db)):
    print(supplier)
    crud.add_supplier(db, supplier)
    db.commit()
    supplier_id = crud.get_last_Supplier(db).SupplierID
    db_supplier = crud.get_supplier(db, supplier_id)
    return db_supplier


@router.put("/suppliers/{supplier_id}")
async def update_supplier(supplier_id: PositiveInt, supplier: dict, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    else:
        if supplier != {}:
            crud.update_supplier(db, supplier, supplier_id)
            db.commit()
        db_supplier = crud.get_supplier(db, supplier_id)
        return db_supplier


@router.delete("/suppliers/{supplier_id}", status_code=204)
async def delete_supplier(supplier_id: PositiveInt, db: Session = Depends(get_db)):
    db_supplier = crud.get_supplier(db, supplier_id)
    if db_supplier is None:
        raise HTTPException(status_code=404, detail="Supplier not found")
    else:
        crud.delete_supplier(db,supplier_id)
        db.commit()



