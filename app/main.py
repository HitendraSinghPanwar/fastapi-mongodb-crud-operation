from fastapi import FastAPI, HTTPException
from .models import UserCreate, UserUpdate, User, Product, ProductCreate, ProductUpdate, Purchase
from .mongodb import collection, products_collection, purchases_collection
from datetime import datetime
from bson import ObjectId
from email_validator import validate_email, EmailNotValidError

app = FastAPI()

@app.post("/users/", response_model=User)
async def create_user(user: UserCreate):
    try:
        validate_email(user.email)
    except EmailNotValidError:
        raise HTTPException(status_code=400, detail="Invalid email address")

    existing = await collection.find_one({"email": user.email})
    if existing:
        raise HTTPException(status_code=409, detail="Email already registered")

    result = await collection.insert_one(user.dict())
    return {"id": str(result.inserted_id), **user.dict()}

@app.get("/users/", response_model=list[User])
async def get_users():
    users = await collection.find().to_list(100)
    return [{"id": str(u["_id"]), **{k: v for k, v in u.items() if k != "_id"}} for u in users]

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: str):
    try:
        user = await collection.find_one({"_id": ObjectId(user_id)})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": str(user["_id"]), **{k: v for k, v in user.items() if k != "_id"}}
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@app.put("/users/{user_id}", response_model=User)
async def update_user(user_id: str, user: UserUpdate):
    try:
        result = await collection.update_one({"_id": ObjectId(user_id)}, {"$set": user.dict(exclude_unset=True)})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")

        updated = await collection.find_one({"_id": ObjectId(user_id)})
        return {"id": str(updated["_id"]), **{k: v for k, v in updated.items() if k != "_id"}}
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@app.delete("/users/{user_id}")
async def delete_user(user_id: str):
    try:
        result = await collection.delete_one({"_id": ObjectId(user_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        return {"detail": "User deleted"}
    except:
        raise HTTPException(status_code=400, detail="Invalid user ID")

@app.post("/products/", response_model=Product)
async def create_product(product: ProductCreate):
    result = await products_collection.insert_one(product.dict())
    return {"id": str(result.inserted_id), **product.dict()}

@app.get("/products/", response_model=list[Product])
async def get_products():
    products = await products_collection.find().to_list(100)
    return [{"id": str(p["_id"]), **{k: v for k, v in p.items() if k != "_id"}} for p in products]

@app.put("/products/{product_id}", response_model=Product)
async def update_product(product_id: str, product: ProductUpdate):
    try:
        result = await products_collection.update_one({"_id": ObjectId(product_id)}, {"$set": product.dict(exclude_unset=True)})
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")

        updated = await products_collection.find_one({"_id": ObjectId(product_id)})
        return {"id": str(updated["_id"]), **{k: v for k, v in updated.items() if k != "_id"}}
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")

@app.delete("/products/{product_id}")
async def delete_product(product_id: str):
    try:
        result = await products_collection.delete_one({"_id": ObjectId(product_id)})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Product not found")
        return {"detail": "Product deleted"}
    except:
        raise HTTPException(status_code=400, detail="Invalid product ID")

@app.post("/purchase/")
async def create_purchase(purchase: Purchase):
    try:
        purchase_doc = {
            "user_id": ObjectId(purchase.user_id),
            "product_id": ObjectId(purchase.product_id),
            "purchase_date": purchase.purchase_date or datetime.utcnow()
        }
        await purchases_collection.insert_one(purchase_doc)
        return {"detail": "Purchase recorded"}
    except:
        raise HTTPException(status_code=400, detail="Invalid purchase data")

@app.get("/users-purchases/")
async def users_purchases():
    pipeline = [
        {"$lookup": {
            "from": "purchases",
            "localField": "_id",
            "foreignField": "user_id",
            "as": "purchases"
        }},
        {"$unwind": {"path": "$purchases", "preserveNullAndEmptyArrays": True}},
        {"$lookup": {
            "from": "products",
            "localField": "purchases.product_id",
            "foreignField": "_id",
            "as": "product_info"
        }},
        {"$unwind": {"path": "$product_info", "preserveNullAndEmptyArrays": True}},
        {"$group": {
            "_id": "$_id",
            "name": {"$first": "$name"},
            "email": {"$first": "$email"},
            "is_active": {"$first": "$is_active"},
            "purchased_products": {
                "$push": {
                    "name": "$product_info.name",
                    "category": "$product_info.category",
                    "price": "$product_info.price"
                }
            }
        }}
    ]

    results = await collection.aggregate(pipeline).to_list(length=100)
    return [{"id": str(r["_id"]), **{k: v for k, v in r.items() if k != "_id"}} for r in results]
