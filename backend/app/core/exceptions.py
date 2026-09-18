class ProviderError(Exception):
    def __init__(self, message: str, *, retryable: bool = True) -> None:
        super().__init__(message)
        self.retryable = retryable


class ProviderMalformedResponse(ProviderError):
    pass


class MLUnavailableError(Exception):
    pass


class RuntimeDataError(Exception):
    pass
