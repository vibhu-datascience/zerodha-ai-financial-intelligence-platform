import os
from datetime import datetime, timedelta, timezone

from jose import jwt
from passlib.context import CryptContext


class AuthService:

    def __init__(self):

        self.secret_key = os.getenv(
            "JWT_SECRET_KEY",
            "zerodha-ai-development-secret-key"
        )

        self.algorithm = "HS256"

        self.access_token_expire_minutes = int(
            os.getenv(
                "JWT_ACCESS_TOKEN_EXPIRE_MINUTES",
                "60"
            )
        )

        self.password_context = CryptContext(
            schemes=["bcrypt"],
            deprecated="auto"
        )

    def hash_password(self, password: str) -> str:

        return self.password_context.hash(password)

    def verify_password(
        self,
        plain_password: str,
        password_hash: str
    ) -> bool:

        return self.password_context.verify(
            plain_password,
            password_hash
        )

    def create_access_token(
        self,
        username: str
    ) -> str:

        expire = (
            datetime.now(timezone.utc)
            + timedelta(
                minutes=self.access_token_expire_minutes
            )
        )

        payload = {
            "sub": username,
            "exp": expire
        }

        return jwt.encode(
            payload,
            self.secret_key,
            algorithm=self.algorithm
        )

    def decode_access_token(
        self,
        token: str
    ):

        try:

            payload = jwt.decode(
                token,
                self.secret_key,
                algorithms=[self.algorithm]
            )

            username = payload.get("sub")

            if not username:
                return None

            return username

        except Exception:

            return None