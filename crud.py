from sqlalchemy.orm import Session

import models
import schemas


def get_shippers(db: Session):
    return db.query(models.Shipper).all()


def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models.Shipper).filter(models.Shipper.ShipperID == shipper_id).first()
    )


def get_suppliers(db: Session):
    return db.query(models.Supplier).order_by(models.Supplier.SupplierID.asc()).all()


def get_supplier(db: Session, supplier_id: int):
    return (
        db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).first()
    )


def get_products (db: Session, supplier_id: int):
    return (
        db.query(models.Product).filter(models.Product.SupplierID == supplier_id).all()
    )


def get_product_category(db: Session, category_id: int):
    return(
        db.query(models.Category).filter(models.Category.CategoryID == category_id).first()
    )


def get_last_Supplier(db:Session):
    return (
        db.query(models.Supplier).order_by(models.Supplier.SupplierID.desc()).first()
    )


def add_supplier(db:Session, supplier: schemas.Supplier):
    last_id = db.query(models.Supplier).order_by(models.Supplier.SupplierID.desc()).first()
    s = models.Supplier(SupplierID = last_id.SupplierID+1,CompanyName = supplier.CompanyName,ContactName = supplier.ContactName,
                        ContactTitle = supplier.ContactTitle, Address = supplier.Address, City = supplier.City,
                        Region = supplier.Region, PostalCode = supplier.PostalCode,Country = supplier.Country,
                        Phone = supplier.Phone, Fax = supplier.Fax, HomePage = supplier.HomePage)
    print(s.SupplierID)
    return (
        db.add(s)
    )


def update_supplier(db:Session, supplier: dict, supplier_id: int):
    return (
        db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).update(supplier, synchronize_session="fetch")
    )

def delete_supplier(db:Session,  supplier_id: int):
    return (
        db.delete(db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).first())
    )