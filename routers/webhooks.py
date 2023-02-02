import os
import json
from datetime import datetime


from fastapi import APIRouter, HTTPException, Header, Request

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    MessageEvent, 
    TextMessage, TextSendMessage, 
    StickerMessage, StickerSendMessage
)

from pydantic import BaseModel

from typing import List, Optional

from firebase_admin import db
# from . import database

line_bot_api = LineBotApi( os.getenv('LINE_CHANNEL_ACCESS_TOKEN') )
handler = WebhookHandler( os.getenv('LINE_CHANNEL_SECRET') )


router = APIRouter(
    prefix="/line",
    tags=["chatbot"],
    responses={404: {"description": "Not found"}},
)

class Line(BaseModel):
    destination: str
    events: List[Optional[None]]

@router.post("/")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(status_code=400, detail="chatbot handle body error.")
    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    print("!!!!!!!!!!!!!!!!!!!!!!")
    print(event)
    print( event.source )

    user_id = db.reference( f'users/{event.source.user_id}/messages' )
    user_id.push({
        "text": event.message.text,
        "timestamp":  event.timestamp
    })

    print("!!!!!!!!!!!!!!!!!!!!!!")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )