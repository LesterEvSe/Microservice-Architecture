from Entity.User import *
from Data.UserDTO import *

def json_to_user_dto(json_data):
    try:
        username = json_data.get("username")
        email = json_data.get("email")
        password = json_data.get("password")

        if not username or not email or not password:
            raise ValueError("Incomplete user data")

        return (True, UserDTO(username=username, email=email, password=password))
    except (TypeError, ValueError) as e:
        return (False, f"error when extracting data: {e}")

def dto_to_user_entity(user_dto: UserDTO):
    return User(username=user_dto.username, email=user_dto.email, password=user_dto.password, jwt_token=None)

def user_entity_to_dto(user: User):
    return UserDTO(username=user.username, email=user.email, password=user.password)