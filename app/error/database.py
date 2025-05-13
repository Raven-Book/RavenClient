class UnsupportedDatabaseError(Exception):
    def __init__(self, db_type, message=None):
        self.db_type = db_type
        self.message = message or f"Database type '{db_type}' is not supported."
        super().__init__(self.message)
