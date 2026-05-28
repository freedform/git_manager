class Result:
    def __init__(
        self,
        result: str,
        status: str = "success",
        error: str = None,
    )-> None:
        self.status = status
        self.result = result
        self.error = error
        self.lines = result.splitlines() if result else []
        