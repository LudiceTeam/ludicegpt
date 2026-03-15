from jose import JWTError, jwt
from datetime import timedelta, datetime, timezone
import os
from dotenv import load_dotenv

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
refresh_token_key = os.getenv("REFRESH_SECRET_KEY")
algorithm = os.getenv("ALGORITHM")

access_token_exp_min = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
refresh_token_exp_days = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


def create_access_token(data: dict) -> str:
    """Генерирует короткоживущий access token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=access_token_exp_min)
    to_encode.update({"exp": expire, "type": "access"})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def create_refresh_token(data: dict) -> str:
    """Генерирует долгоживущий refresh token."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=refresh_token_exp_days)
    to_encode.update({"exp": expire, "type": "refresh"})
    encoded_jwt = jwt.encode(to_encode, refresh_token_key, algorithm=algorithm)
    return encoded_jwt