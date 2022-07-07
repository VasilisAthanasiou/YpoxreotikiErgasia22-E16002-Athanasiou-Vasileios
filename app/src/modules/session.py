class User:
    def __init__(self, id):
        self.id = id
        self.is_active = True
        self.authenticated

    def get_id(self):
        return self.id