from fastapi import APIRouter, HTTPException
import requests
from database import get_db_connection

router = APIRouter()

# WhatsApp API credentials (replace with actual credentials)
WHATSAPP_API_URL = "https://graph.facebook.com/v17.0/YOUR_PHONE_NUMBER_ID/messages"
ACCESS_TOKEN = "YOUR_ACCESS_TOKEN"

def send_whatsapp_message(user_id: str, message: str):
    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": user_id,
        "type": "text",
        "text": {"body": message}
    }
    response = requests.post(WHATSAPP_API_URL, json=payload, headers=headers)
    return response.json()

@router.get("/browse_products")
def browse_products(category: str = None):
    conn = get_db_connection()
    cursor = conn.cursor()
    if category:
        cursor.execute("SELECT p.name, p.price, p.image_url, c.name AS category FROM products p JOIN categories c ON p.category_id = c.id WHERE c.name = ?", (category,))
    else:
        cursor.execute("SELECT p.name, p.price, p.image_url, c.name AS category FROM products p JOIN categories c ON p.category_id = c.id")
    products = cursor.fetchall()
    conn.close()
    
    if not products:
        return {"message": "No products found."}
    
    product_list = "Available Products:\n"
    for product in products:
        product_list += f"- {product['name']} (${product['price']}) - Category: {product['category']}\n"
    
    return {"products": product_list}

@router.post("/whatsapp/browse")
def whatsapp_browse(user_id: str, category: str = None):
    products_response = browse_products(category)
    send_whatsapp_message(user_id, products_response["products"])
    return {"message": "Products sent to WhatsApp."}