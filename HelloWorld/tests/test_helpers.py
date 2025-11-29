from crud import create_user, list_users, paginate_users, filter_users_by_age


def test_list_and_pagination(session):
    # create 5 users
    for i in range(5):
        create_user(session, f'U{i}', 20 + i)

    all_users = list_users(session)
    assert len(all_users) == 5

    pag1 = paginate_users(session, page=1, per_page=2)
    assert pag1['page'] == 1
    assert pag1['per_page'] == 2
    assert len(pag1['items']) == 2

    pag3 = paginate_users(session, page=3, per_page=2)
    # 5 items with 2 per page => page3 has 1 item
    assert len(pag3['items']) == 1


def test_filter_by_age(session):
    create_user(session, 'young', 18)
    create_user(session, 'mid', 25)
    create_user(session, 'old', 30)

    res = filter_users_by_age(session, min_age=20)
    assert all(u.age >= 20 for u in res)

    res2 = filter_users_by_age(session, max_age=25)
    assert all(u.age <= 25 for u in res2)
