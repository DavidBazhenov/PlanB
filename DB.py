
def getUser(user_id, auth):
    try:
        # Получение информации о пользователе
        user = auth.get_user(user_id)
        return user
    except:
        return False

