class Result:
    def __init__(self, stdout: str, ok: bool = True, error: str = None) -> None:
        self.ok = ok
        self.stdout = stdout
        self.error = error
        self.lines = stdout.splitlines() if stdout else []

    def __repr__(self) -> str:
        if self.ok:
            return f"Result(ok=True, stdout={self.stdout!r})"
        return f"Result(ok=False, error={self.error!r})"
