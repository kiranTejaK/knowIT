import secrets
from datetime import datetime, timedelta, timezone
from typing import Tuple
import structlog
from app.core import security
from app.core.config import settings
from app.core.exceptions import (
    ConflictException,
    NotFoundException,
    UnauthorizedException,
    ValidationException,
)
from app.models.token import EmailVerificationToken, PasswordResetToken, RefreshToken
from app.models.user import User
from app.providers.email.email_provider import EmailProvider
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, UserCreate

logger = structlog.get_logger(__name__)


class AuthService:
    def __init__(self, user_repo: UserRepository, email_provider: EmailProvider):
        self.user_repo = user_repo
        self.email_provider = email_provider

    async def register(self, user_in: UserCreate) -> User:
        existing_user = await self.user_repo.get_by_email(user_in.email)
        if existing_user:
            raise ConflictException("User with this email already exists")

        hashed_password = security.get_password_hash(user_in.password)
        user = User(
            email=user_in.email,
            password_hash=hashed_password,
            full_name=user_in.full_name,
            is_email_verified=False,
            is_active=True,
        )
        user = await self.user_repo.create(user)

        # Generate Verification Token
        raw_token = secrets.token_urlsafe(32)
        hashed_t = security.hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.EMAIL_VERIFICATION_EXPIRE_HOURS)

        v_token = EmailVerificationToken(
            user_id=user.id,
            token_hash=hashed_t,
            expires_at=expires_at,
        )
        await self.user_repo.create_verification_token(v_token)
        self.email_provider.send_verification_email(user.email, raw_token)

        logger.info("User registered successfully", user_id=str(user.id), email=user.email)
        return user

    async def verify_email(self, raw_token: str) -> bool:
        token_hash = security.hash_token(raw_token)
        token_record = await self.user_repo.get_verification_token(token_hash)
        if not token_record:
            raise ValidationException("Invalid or expired verification token")

        if token_record.expires_at < datetime.now(timezone.utc):
            raise ValidationException("Verification token has expired")

        user = await self.user_repo.get_by_id(token_record.user_id)
        if not user:
            raise NotFoundException("User")

        user.is_email_verified = True
        await self.user_repo.update(user)
        await self.user_repo.mark_verification_token_used(token_record)

        logger.info("Email verified successfully", user_id=str(user.id))
        return True

    async def login(self, login_in: LoginRequest) -> Tuple[str, str, User]:
        user = await self.user_repo.get_by_email(login_in.email)
        if not user or not security.verify_password(login_in.password, user.password_hash):
            raise UnauthorizedException("Incorrect email or password")

        if not user.is_active:
            raise UnauthorizedException("Inactive user account")

        user.last_login_at = datetime.now(timezone.utc)
        await self.user_repo.update(user)

        access_token = security.create_access_token(subject=str(user.id))

        raw_refresh_token = secrets.token_urlsafe(32)
        hashed_refresh = security.hash_token(raw_refresh_token)
        expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=hashed_refresh,
            expires_at=expires_at,
        )
        await self.user_repo.create_refresh_token(refresh_record)

        logger.info("User logged in successfully", user_id=str(user.id))
        return access_token, raw_refresh_token, user

    async def refresh_tokens(self, raw_refresh_token: str) -> Tuple[str, str, User]:
        token_hash = security.hash_token(raw_refresh_token)
        token_record = await self.user_repo.get_refresh_token(token_hash)
        if not token_record or token_record.expires_at < datetime.now(timezone.utc):
            raise UnauthorizedException("Invalid or expired refresh token")

        user = await self.user_repo.get_by_id(token_record.user_id)
        if not user or not user.is_active:
            raise UnauthorizedException("User unavailable")

        # Refresh Token Rotation
        await self.user_repo.revoke_refresh_token(token_record)

        new_access_token = security.create_access_token(subject=str(user.id))
        new_raw_refresh_token = secrets.token_urlsafe(32)
        new_hashed_refresh = security.hash_token(new_raw_refresh_token)
        new_expires_at = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)

        new_refresh_record = RefreshToken(
            user_id=user.id,
            token_hash=new_hashed_refresh,
            expires_at=new_expires_at,
        )
        await self.user_repo.create_refresh_token(new_refresh_record)

        logger.info("Refresh token rotated successfully", user_id=str(user.id))
        return new_access_token, new_raw_refresh_token, user

    async def logout(self, raw_refresh_token: str) -> None:
        token_hash = security.hash_token(raw_refresh_token)
        token_record = await self.user_repo.get_refresh_token(token_hash)
        if token_record:
            await self.user_repo.revoke_refresh_token(token_record)
            logger.info("Refresh token revoked", user_id=str(token_record.user_id))

    async def forgot_password(self, email: str) -> None:
        user = await self.user_repo.get_by_email(email)
        if not user:
            logger.info("Forgot password requested for non-existent email", email=email)
            return

        raw_token = secrets.token_urlsafe(32)
        token_hash = security.hash_token(raw_token)
        expires_at = datetime.now(timezone.utc) + timedelta(hours=settings.PASSWORD_RESET_EXPIRE_HOURS)

        reset_token = PasswordResetToken(
            user_id=user.id,
            token_hash=token_hash,
            expires_at=expires_at,
        )
        await self.user_repo.create_password_reset_token(reset_token)
        self.email_provider.send_password_reset_email(user.email, raw_token)

        logger.info("Password reset email sent", user_id=str(user.id))

    async def reset_password(self, raw_token: str, new_password: str) -> None:
        token_hash = security.hash_token(raw_token)
        token_record = await self.user_repo.get_password_reset_token(token_hash)
        if not token_record or token_record.expires_at < datetime.now(timezone.utc):
            raise ValidationException("Invalid or expired password reset token")

        user = await self.user_repo.get_by_id(token_record.user_id)
        if not user:
            raise NotFoundException("User")

        user.password_hash = security.get_password_hash(new_password)
        await self.user_repo.update(user)
        await self.user_repo.mark_password_reset_token_used(token_record)
        await self.user_repo.revoke_all_user_refresh_tokens(user.id)

        logger.info("Password reset successful", user_id=str(user.id))
