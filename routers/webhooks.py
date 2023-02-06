import os
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

from typing import Optional

from firebase_admin import db
# from . import database

line_bot_api = LineBotApi(os.getenv('LINE_CHANNEL_ACCESS_TOKEN'))
handler = WebhookHandler(os.getenv('LINE_CHANNEL_SECRET'))


router = APIRouter(
    prefix="/line",
    tags=["chatbot"],
    responses={404: {"description": "Not found"}},
)


class Line(BaseModel):
    destination: str
    events: list[Optional[None]]


@router.post("/")
async def callback(request: Request, x_line_signature: str = Header(None)):
    body = await request.body()
    print(body)
    try:
        handler.handle(body.decode("utf-8"), x_line_signature)
    except InvalidSignatureError:
        raise HTTPException(
            status_code=400, detail="chatbot handle body error.")
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def message_text(event):
    print("!!!!!!!!!!!!!!!!!!!!!!")
    print(event)
    print(event.source)

    user_id = db.reference(f'users/{event.source.user_id}/messages')
    user_id.push({
        "text": event.message.text,
        "timestamp":  event.timestamp
    })

    print("!!!!!!!!!!!!!!!!!!!!!!")
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )


class Message(BaseModel):
    user_name: str
    text: str
    timestamp: datetime | None


async def load_users():
    ref_users = db.reference("/users").get()
    users = []

    messages = []
    for user_id, value in ref_users.items():
        profile = line_bot_api.get_profile(user_id)
        users.append(profile)

        for key in value['messages']:
            ts = datetime.fromtimestamp(
                value['messages'][key]['timestamp']/1000.0
            )

            m = Message(
                text=value['messages'][key]['text'],
                timestamp=ts,
                user_name=profile.display_name
            )
            messages.append(m)

    return users, messages
