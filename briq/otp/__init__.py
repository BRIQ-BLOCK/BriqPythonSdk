"""
OTP module for the Briq API — Phase 5.
All routes under /v1/otp/
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..client import Client


class OtpAPI:
    """
    OTP (One-Time Password) API for Briq.

    Provides methods for requesting, verifying, resending, invalidating,
    and checking the status of OTPs.
    """

    def __init__(self, client: Client) -> None:
        self.client = client

    def request(
        self,
        phone_number: str,
        app_key: str,
        sender_id: str | None = None,
        otp_length: int = 6,
        minutes_to_expire: int = 10,
        delivery_method: str = "sms",
        message_template: str | None = None,
    ) -> dict:
        """
        POST /v1/otp/request — request a new OTP.

        Args:
            phone_number (str): Recipient's phone number (e.g. "+255712345678")
            app_key (str): Developer app key
            sender_id (str, optional): SMS sender ID (defaults to "BRIQ OTP")
            otp_length (int): Length of OTP code (default 6)
            minutes_to_expire (int): OTP expiry in minutes (default 10)
            delivery_method (str): "sms" or "call" (default "sms")
            message_template (str, optional): Custom template, use {code} placeholder

        Returns:
            dict: BaseResponse with success, message, data
        """
        data = {
            "phone_number": phone_number,
            "app_key": app_key,
            "otp_length": otp_length,
            "minutes_to_expire": minutes_to_expire,
            "delivery_method": delivery_method,
        }
        if sender_id is not None:
            data["sender_id"] = sender_id
        if message_template is not None:
            data["message_template"] = message_template
        return self.client.post("otp/request", data=data)

    def verify(self, phone_number: str, app_key: str, code: str) -> dict:
        """
        POST /v1/otp/verify — verify an OTP code.

        Args:
            phone_number (str): Recipient's phone number
            app_key (str): Developer app key
            code (str): OTP code to verify

        Returns:
            dict: BaseResponse
        """
        return self.client.post(
            "otp/verify",
            data={
                "phone_number": phone_number,
                "app_key": app_key,
                "code": code,
            },
        )

    def resend(
        self,
        phone_number: str,
        app_key: str,
        sender_id: str | None = None,
        otp_length: int = 6,
        minutes_to_expire: int = 10,
        delivery_method: str = "sms",
        message_template: str | None = None,
    ) -> dict:
        """
        POST /v1/otp/resend — resend an OTP.

        Args:
            phone_number (str): Recipient's phone number
            app_key (str): Developer app key
            sender_id (str, optional): SMS sender ID
            otp_length (int): OTP code length (default 6)
            minutes_to_expire (int): Expiry in minutes (default 10)
            delivery_method (str): "sms" or "call" (default "sms")
            message_template (str, optional): Custom template

        Returns:
            dict: BaseResponse
        """
        data = {
            "phone_number": phone_number,
            "app_key": app_key,
            "otp_length": otp_length,
            "minutes_to_expire": minutes_to_expire,
            "delivery_method": delivery_method,
        }
        if sender_id is not None:
            data["sender_id"] = sender_id
        if message_template is not None:
            data["message_template"] = message_template
        return self.client.post("otp/resend", data=data)

    def invalidate(self, phone_number: str, app_key: str) -> dict:
        """
        POST /v1/otp/invalidate — invalidate any active OTP for a phone number.

        Args:
            phone_number (str): Recipient's phone number
            app_key (str): Developer app key

        Returns:
            dict: BaseResponse
        """
        return self.client.post(
            "otp/invalidate",
            data={
                "phone_number": phone_number,
                "app_key": app_key,
            },
        )

    def status(self, phone_number: str, app_key: str) -> dict:
        """
        GET /v1/otp/status — check OTP status for a phone number.

        Args:
            phone_number (str): Phone number to check
            app_key (str): Developer app key

        Returns:
            dict: BaseResponse
        """
        return self.client.get(
            "otp/status",
            params={
                "phone_number": phone_number,
                "app_key": app_key,
            },
        )
