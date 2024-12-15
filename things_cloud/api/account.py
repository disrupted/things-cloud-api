from __future__ import annotations

import base64
import json
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import quote

import httpx
import pydantic


class Credentials(pydantic.BaseModel):
    email: pydantic.EmailStr
    password: pydantic.SecretStr

    def as_encoded_payload(self) -> str:
        payload = json.dumps(
            {"ep": {"e": self.email, "p": self.password.get_secret_value()}}
        ).encode("utf-8")
        return base64.b64encode(payload).decode("utf-8")


class AccountStatus(StrEnum):
    ACTIVE = "SYAccountStatusActive"


class AccountInfo(pydantic.BaseModel):
    sla_version_accepted: str = pydantic.Field(
        alias="SLA-version-accepted"
    )  # TODO: deserialize to int?
    email: pydantic.EmailStr
    history_key: pydantic.UUID4 = pydantic.Field(alias="history-key")
    issues: list
    maildrop_email: pydantic.EmailStr = pydantic.Field(alias="maildrop-email")
    status: AccountStatus


class SharedSession(pydantic.BaseModel):
    head_index: int = pydantic.Field(alias="headIndex")
    history_key_session_secret: str = pydantic.Field(alias="historyKeySessionSecret")


@dataclass
class Account:
    _credentials: Credentials
    _info: AccountInfo

    @classmethod
    def login(cls, credentials: Credentials) -> Account:
        response = httpx.get(
            f"https://cloud.culturedcode.com/version/1/account/{credentials.email}",
            headers={
                "Authorization": f"Password {quote(credentials.password.get_secret_value(), safe="'")}",
            },
        )
        # TODO: handle 401 Unauthorized
        if not response.is_success:
            print(response.status_code, response.read())
            raise RuntimeError()
        content = response.json()
        info = AccountInfo.model_validate(content)
        return Account(_credentials=credentials, _info=info)

    def new_session(self) -> SharedSession:
        response = httpx.post(
            "https://cloud.culturedcode.com/api/account/login/getT3SharedSession",
            headers={
                "Authorization": f"B64SON {self._credentials.as_encoded_payload()}"
            },
        )
        if not response.is_success:
            print(response.status_code, response.read())
            raise RuntimeError()
        content = response.json()
        return SharedSession.model_validate(content)
