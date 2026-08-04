class VendorVerseException(Exception):
    """Base exception for all custom VendorVerse errors."""
    pass

class BusinessRuleError(VendorVerseException):
    """Raised when a business rule is violated (e.g., insufficient stock)."""
    pass

class ResourceNotFoundError(VendorVerseException):
    """Raised when a requested resource is not found by a service."""
    pass

class UnauthorizedActionError(VendorVerseException):
    """Raised when a user is not authorized to perform an action."""
    pass
