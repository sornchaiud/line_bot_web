import os

import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
import json

from fastapi import status, APIRouter, HTTPException, Header, Request

from typing import Union
from pydantic import BaseModel

router = APIRouter(
    prefix="/items",
    tags=["database"],
    responses={404: {"description": "Not found"}},
)

class Item(BaseModel):
    id: int
    name: str
    price: Union[float, None] = None
    is_offer: Union[bool, None] = None

cred = credentials.Certificate(os.getenv('FIREBASE_KEY'))
default_app = firebase_admin.initialize_app(cred, {
    'databaseURL':os.getenv('databaseURL')
})

# ref = db.reference("/Books")
# with open("books.json", "r") as f:
#     file_contents = json.load(f)
# ref.set(file_contents)

@router.get("/{item_id}")
async def read_item(item_id: int, q: Union[str, None] = None):
    ref_item = db.reference("/items/"+str(item_id)).get()
    return ref_item

@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_item(item: Item):
    ref_item = db.reference("/items/"+str(item.id))
    ref_item.set(item.dict())

    return {"item_name": item.name, "item_id": item.id, "price": item.price}

@router.put("/{item_id}", status_code=status.HTTP_200_OK)
async def update_item(item_id: int, item: Item):
    ref_item = db.reference("/items/"+str(item_id))
    item.id = item_id
    ref_item.update(item.dict())
    return ref_item.get()
