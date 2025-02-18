# main.py
from fastapi import FastAPI
from products import router as products_router
from userBrowse import router as userBrowse_router

app = FastAPI()

# Include Admin Routes
app.include_router(products_router)
app.include_router(userBrowse_router)