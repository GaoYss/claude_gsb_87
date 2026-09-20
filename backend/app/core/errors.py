"""领域异常：服务层抛业务错误，接口层统一翻译成 HTTP 响应。"""


class DomainError(Exception):
    """业务规则未满足。"""

    status_code = 400
    code = "domain_error"

    def __init__(self, message: str, *, code: str | None = None) -> None:
        super().__init__(message)
        self.message = message
        if code:
            self.code = code


class NotFoundError(DomainError):
    """资源不存在。"""

    status_code = 404
    code = "not_found"


class ConflictError(DomainError):
    """资源冲突或状态不允许的操作。"""

    status_code = 409
    code = "conflict"


class InvalidOperationError(DomainError):
    """参数合法但业务上不允许。"""

    status_code = 422
    code = "invalid_operation"

