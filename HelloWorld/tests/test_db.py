from db_sqlalchemy import User


def test_user_insert_and_query(session):
    # Insert a user using the shared in-memory session fixture
    u = User(name='TestUser', age=42)
    session.add(u)
    session.commit()

    # Query and assert
    users = session.query(User).all()
    assert len(users) == 1
    assert users[0].name == 'TestUser'
    assert users[0].age == 42


def test_user_factory(db):
    # Use the db fixture helper to create users
    user = db.create_user(name='FactoryUser', age=33)
    assert user.id is not None

    users = db.all_users()
    # There may be previous rows from other tests, but our created user should be present
    assert any(u.name == 'FactoryUser' and u.age == 33 for u in users)
