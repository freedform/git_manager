class MainStatus:
    def __init__(self, base_dir: str = "", repos: dict = None) -> None:
        self.base_dir = base_dir
        self.repos = repos if repos is not None else {}

    def __str__(self) -> str:
        return f"Base directory: {self.base_dir}  |  Repositories found: {len(self.repos)}"
