from fastapi import Security, HTTPException
from fastapi.security import APIKeyHeader

from ntm.core.config import get_settings

api_key_header = APIKeyHeader(name=get_settings().api_key_header, auto_error=False)


async def verify_api_key(key: str = Security(api_key_header)):
    settings = get_settings()
    if key != settings.api_key:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key
