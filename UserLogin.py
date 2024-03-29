import DB as db

class UserLogin():
    def fromDB(self, user_id, auth):
        self.__user = db.getUser(user_id, auth)
        return self
    def create(self, user ):
        self.__user = user
        return self
    def is_authenticated(self):
        return True
    def is_active(self):
        return True
    def is_anonymus(self):
        return False
    def get_id(self):
        return str(self.__user['localId'])