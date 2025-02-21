from typing import Optional
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Depends
import shutil
import os
import sqlite3
from pydantic import BaseModel
from database import get_db_connection, UPLOAD_FOLDER

router = APIRouter()

class CategoryRequest(BaseModel):
    name: str

class ProductRequest(BaseModel):
    name: str
    price: float
    category_id: int

@router.post("/add_category")
def add_category(category: CategoryRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO categories (name) VALUES (?)", (category.name,))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        raise HTTPException(status_code=400, detail="Category already exists")
    conn.close()
    return {"message": "Category added successfully"}

@router.post("/upload_image")
def upload_image(file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"message": "Image uploaded successfully", "image_url": f"/{UPLOAD_FOLDER}/{file.filename}"}

@router.post("/add_product")
async def add_product(
    name: str = Form(...),
    price: float = Form(...),
    category_id: int = Form(...),
    image_url: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    # If an image file is uploaded, save it
    if file:
        file_path = os.path.join(UPLOAD_FOLDER, file.filename)
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        image_url = f"/{UPLOAD_FOLDER}/{file.filename}"  # Overwrite image_url with uploaded file

    # Ensure that at least one image source is provided
    if not image_url:
        raise HTTPException(status_code=400, detail="Either an image file or image URL must be provided.")

    # Insert product into the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO products (name, price, image_url, category_id) VALUES (?, ?, ?, ?)",
        (name, price, image_url, category_id)
    )
    conn.commit()
    conn.close()

    return {"message": "Product added successfully", "image_url": image_url}

@router.get("/view_products")
def view_products():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    conn.close()
    return {"products": [dict(product) for product in products]}

@router.put("/update_product/{product_id}")
def update_product(product_id: int, product: ProductRequest):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE products SET name = ?, price = ?, category_id = ? WHERE id = ?", 
                   (product.name, product.price, product.category_id, product_id))
    conn.commit()
    conn.close()
    return {"message": "Product updated successfully"}

@router.delete("/delete_product/{product_id}")
def delete_product(product_id: int):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
    conn.commit()
    conn.close()
    return {"message": "Product deleted successfully"}