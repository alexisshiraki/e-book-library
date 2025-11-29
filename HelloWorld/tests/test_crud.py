from crud import create_user, get_user, update_user_age, delete_user


def test_update_user(session):
    # create
    u = create_user(session, name='UpdUser', age=20)
    assert u.id is not None

    # update
    updated = update_user_age(session, u.id, 25)
    assert updated is not None
    assert updated.age == 25


def test_delete_user(session):
    u = create_user(session, name='DelUser', age=40)
    uid = u.id
    assert get_user(session, uid) is not None

    ok = delete_user(session, uid)
    assert ok is True
    assert get_user(session, uid) is None
