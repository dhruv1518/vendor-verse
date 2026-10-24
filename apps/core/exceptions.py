class VendoraException(Exception):
    """Base exception for all custom Vendora errors."""
    pass

class BusinessRuleError(VendoraException):
    """Raised when a business rule is violated (e.g., insufficient stock)."""
    pass

class ResourceNotFoundError(VendoraException):
    """Raised when a requested resource is not found by a service."""
    pass

class UnauthorizedActionError(VendoraException):
    """Raised when a user is not authorized to perform an action."""
    pass
