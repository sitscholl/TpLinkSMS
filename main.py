from typing import List
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field

import logging
import logging.config
from pathlib import Path

from src.config import load_config
from src.router import Router

config = load_config(Path(__file__).parent / "config/config.yaml")
logging.config.dictConfig(config['logging'])
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TP-Link Router based SMS Api",
    description="Send SMS from the TP-Link router UI",
    version="1.0.0"
)

class SmsRequest(BaseModel):
    to: List[str] = Field(min_items=1)
    message: str = Field(min_length=1, max_length=160)  # TP-Link often ~ 3x 160 chars

def get_router():
    """
    Dependency to get database instance with proper connection management.
    Uses async context manager to ensure database is properly connected and disconnected.
    """
    return Router(**config['general'])

@app.post("/send-sms")
async def send_sms(payload: SmsRequest, router: Router = Depends(get_router)):
    try:
        await router.send_sms(payload.to, payload.message)
        logger.info('Sms sent')
        return {"status": "ok"}
    except Exception as e:
        logger.error(f"Error sending sms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

