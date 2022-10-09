class UserLogin:
    def fromDB(self, user_id, db):
        self.__user = db.getUser(user_id)
        return self.__user

    def create(self, user):
        self.__user = user
        return self.__user

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.__user['id'])