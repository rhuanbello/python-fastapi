from http import HTTPStatus

from fastapi import FastAPI, HTTPException

from fast_zero.schemas import Message, UserDB, UserList, UserPublic, UserSchema

app = FastAPI()

database: list[UserDB] = []


@app.post('/users/', status_code=HTTPStatus.CREATED, response_model=UserPublic)
def create_user(user: UserSchema):
    user_with_id = UserDB(
        id=len(database) + 1,  # generate an id for the user
        **user.model_dump(),  # extract the data from the pydantic model
    )

    database.append(user_with_id)  # append the user to the database
    return user_with_id


@app.get('/users/', status_code=HTTPStatus.OK, response_model=UserList)
def read_users():
    return {'users': database}


@app.get('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def read_user(user_id: int):
    if user_id - 1 not in range(len(database)):  # check if the user exists
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')
    return database[user_id - 1]


@app.put('/users/{user_id}', status_code=HTTPStatus.OK, response_model=UserPublic)
def update_user(user_id: int, user: UserSchema):
    if user_id - 1 not in range(len(database)):  # check if the user exists
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    user_with_id = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = user_with_id  # this in js =

    return user_with_id


@app.delete('/users/{user_id}', status_code=HTTPStatus.OK, response_model=Message)
def delete_user(user_id: int):
    if user_id - 1 not in range(len(database)):  # check if the user exists
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail='User not found')

    del database[user_id - 1]  # in js = database.splice(user_id - 1, 1)
    return {'message': 'User deleted'}
