
    def __init__(self, root: str = "./static"):
        self.root = root
        self._ensure_root()

    def _ensure_root(self):
        self.root = path
        self._ensure_root()

    def serve(self, filename: str) -> Optional[Response]:
        root_path = Path(self.root)
        if not root_path.exists():
            return []
        return [f.name for f in root_path.iterdir() if f.is_file()]
