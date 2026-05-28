class MainStatus:
    def __init__(
        self, 
        base_dir: str = "", 
        repo_list: list = {},
    ) -> None:
        self.base_dir = base_dir
        self.repo_list = repo_list
    
    def get_status(self):
        return {
            "current_base_directory": self.base_dir,
            "found_repositories": len(self.repo_list),
        }