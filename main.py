from typing import List, Union
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, Field, field_validator

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
    version="1.1.0"
)

class SmsRequest(BaseModel):
    message: str = Field(min_length=1, max_length=160)
    to: Union[str, List[str]]

    # Accept extra fields without error
    model_config = {
        "extra": "ignore"
    }

    @field_validator("to")
    def normalize_to_list(cls, v):
        # Case 1: already a list
        if isinstance(v, list):
            # Ensure all items are strings and stripped
            return [str(item).strip() for item in v if str(item).strip()]
        
        # Case 2: single string
        if isinstance(v, str):
            # Split by comma or semicolon
            parts = [p.strip() for p in v.replace(";", ",").split(",")]
            # Filter out empty items
            return [p for p in parts if p]
        
        raise TypeError("Invalid type for 'to': must be string or list of strings")

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

