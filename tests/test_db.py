from sqlalchemy import select

from fast_zero.models import User


def test_create_user(session):  # receives the session from the generator
    user = User(username='rhuanbello', email='rhuanbello@gmail.com', password='123456')  # create a user object

    session.add(user)  # insert the user into the session database
    session.commit()  # save the changes
    session.refresh(user)  # sync the user object with the created user on the DB

    result = session.scalar(select(User).where(User.email == 'rhuanbello@gmail.com'))

    assert result.username == 'rhuanbello'
