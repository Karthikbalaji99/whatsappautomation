import random
import string
import time
from datetime import datetime
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional

app = FastAPI(title="Mock WhatsApp API Server")

# In‐memory storage of messages
#   { message_id: { "to": "<phone>", "body": "<text>", "sent_at": <epoch>, "status": "queued"/"sent"/"failed", "reply_history": [...] } }
MESSAGES: Dict[str, Dict] = {}

# Phones for which replies are always suppressed
SUPPRESS_REPLY_FOR = {"+919876543210", "+919876543211"} # I  did this to check if the follow‐up logic works correctly


def _generate_message_id() -> str:
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=10))


class SendRequest(BaseModel):
    to: str
    body: str


class SendResponse(BaseModel):
    message_id: str
    status: str  # always "queued" initially (we simulate sending later)


class StatusResponse(BaseModel):
    message_id: str
    status: str  # "sent" or "failed" 


class ReplyResponse(BaseModel):
    message_id: str
    reply: Optional[str] = None
    timestamp: Optional[str] = None  


@app.post("/mock/send", response_model=SendResponse)
async def mock_send(req: SendRequest):
    msg_id = _generate_message_id()
    now_epoch = time.time()
    MESSAGES[msg_id] = {
        "to": req.to,
        "body": req.body,
        "sent_at": now_epoch,
        "status": "queued",
        "reply_history": []
    }
    return SendResponse(message_id=msg_id, status="queued")


@app.get("/mock/status/{message_id}", response_model=StatusResponse)
async def mock_status(message_id: str):

    if message_id not in MESSAGES:
        raise HTTPException(status_code=404, detail="Message ID not found")

    record = MESSAGES[message_id]
    current_status = record["status"]
    if current_status == "queued":
        record["status"] = "sent" if random.random() < 0.7 else "failed"
    return StatusResponse(message_id=message_id, status=record["status"])


@app.get("/mock/reply/{message_id}", response_model=ReplyResponse)
async def mock_reply(message_id: str):

    if message_id not in MESSAGES:
        raise HTTPException(status_code=404, detail="Message ID not found")

    record = MESSAGES[message_id]
    phone = record["to"]

    # If this phone is in the suppress list, always return no reply (to check follow‐up logic)
    if phone in SUPPRESS_REPLY_FOR:
        return ReplyResponse(message_id=message_id, reply=None, timestamp=None)

    # If already has a reply, return it (randomly choosing the latest one)
    if record["reply_history"]:
        latest = record["reply_history"][-1]
        return ReplyResponse(message_id=message_id, reply=latest["text"], timestamp=latest["timestamp"])

    # Otherwise, randomly decide (30% chance) to reply if status is "sent" (to simulate user engagement)
    if record["status"] == "sent" and random.random() < 0.3:
        possible_replies = [
            "I’m interested, please share more.",
            "Can you tell me about costs?",
            "Thank you, I’d like to apply.",
            "Not now, maybe later."
        ]
        chosen = random.choice(possible_replies)
        ts = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        record["reply_history"].append({"text": chosen, "timestamp": ts})
        return ReplyResponse(message_id=message_id, reply=chosen, timestamp=ts)

    # No reply yet
    return ReplyResponse(message_id=message_id, reply=None, timestamp=None)
