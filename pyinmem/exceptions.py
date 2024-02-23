class PyInMemStoreError(Exception):
    """Base class for all PyInMemStore errors."""


class DataTypeError(PyInMemStoreError):
    """Raised when there is a data type related error."""


class OperationNotSupportedError(PyInMemStoreError):
    """Raised when an operation is not supported for a given data type."""
