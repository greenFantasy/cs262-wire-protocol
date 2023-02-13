from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class AccountCreateReply(_message.Message):
    __slots__ = ["auth_token", "error_code", "fullname", "version"]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    FULLNAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    auth_token: str
    error_code: str
    fullname: str
    version: int
    def __init__(self, version: _Optional[int] = ..., error_code: _Optional[str] = ..., auth_token: _Optional[str] = ..., fullname: _Optional[str] = ...) -> None: ...

class AccountCreateRequest(_message.Message):
    __slots__ = ["fullname", "password", "username", "version"]
    FULLNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    fullname: str
    password: str
    username: str
    version: int
    def __init__(self, version: _Optional[int] = ..., username: _Optional[str] = ..., password: _Optional[str] = ..., fullname: _Optional[str] = ...) -> None: ...

class DeleteAccountReply(_message.Message):
    __slots__ = ["error_code", "version"]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    error_code: str
    version: int
    def __init__(self, version: _Optional[int] = ..., error_code: _Optional[str] = ...) -> None: ...

class DeleteAccountRequest(_message.Message):
    __slots__ = ["auth_token", "username", "version"]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    auth_token: str
    username: str
    version: int
    def __init__(self, version: _Optional[int] = ..., auth_token: _Optional[str] = ..., username: _Optional[str] = ...) -> None: ...

class ListAccountReply(_message.Message):
    __slots__ = ["account_names", "error_code", "version"]
    ACCOUNT_NAMES_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    account_names: str
    error_code: str
    version: int
    def __init__(self, version: _Optional[int] = ..., error_code: _Optional[str] = ..., account_names: _Optional[str] = ...) -> None: ...

class ListAccountRequest(_message.Message):
    __slots__ = ["auth_token", "number_of_accounts", "regex", "username", "version"]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    NUMBER_OF_ACCOUNTS_FIELD_NUMBER: _ClassVar[int]
    REGEX_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    auth_token: str
    number_of_accounts: int
    regex: str
    username: str
    version: int
    def __init__(self, version: _Optional[int] = ..., auth_token: _Optional[str] = ..., username: _Optional[str] = ..., number_of_accounts: _Optional[int] = ..., regex: _Optional[str] = ...) -> None: ...

class LoginReply(_message.Message):
    __slots__ = ["auth_token", "error_code", "fullname", "version"]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    FULLNAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    auth_token: str
    error_code: str
    fullname: str
    version: int
    def __init__(self, version: _Optional[int] = ..., error_code: _Optional[str] = ..., auth_token: _Optional[str] = ..., fullname: _Optional[str] = ...) -> None: ...

class LoginRequest(_message.Message):
    __slots__ = ["password", "username", "version"]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    password: str
    username: str
    version: int
    def __init__(self, version: _Optional[int] = ..., username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class MessageReply(_message.Message):
    __slots__ = ["error_code", "version"]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    error_code: str
    version: int
    def __init__(self, version: _Optional[int] = ..., error_code: _Optional[str] = ...) -> None: ...

class MessageRequest(_message.Message):
    __slots__ = ["auth_token", "message", "recipient_username", "username", "version"]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    RECIPIENT_USERNAME_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    auth_token: str
    message: str
    recipient_username: str
    username: str
    version: int
    def __init__(self, version: _Optional[int] = ..., auth_token: _Optional[str] = ..., username: _Optional[str] = ..., recipient_username: _Optional[str] = ..., message: _Optional[str] = ...) -> None: ...

class RefreshReply(_message.Message):
    __slots__ = ["error_code", "message", "version"]
    ERROR_CODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGE_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    error_code: str
    message: str
    version: int
    def __init__(self, version: _Optional[int] = ..., message: _Optional[str] = ..., error_code: _Optional[str] = ...) -> None: ...

class RefreshRequest(_message.Message):
    __slots__ = ["auth_token", "username", "version"]
    AUTH_TOKEN_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    VERSION_FIELD_NUMBER: _ClassVar[int]
    auth_token: str
    username: str
    version: int
    def __init__(self, version: _Optional[int] = ..., auth_token: _Optional[str] = ..., username: _Optional[str] = ...) -> None: ...
