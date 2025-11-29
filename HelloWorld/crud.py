"""Simple CRUD helper functions for the `User` model.

Functions operate on a provided SQLAlchemy `Session` so tests
can use the in-memory session fixture.
"""
from typing import Optional

from db_sqlalchemy import User


def create_user(session, name: str, age: Optional[int] = None) -> User:
    u = User(name=name, age=age)
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def get_user(session, user_id: int) -> Optional[User]:
    return session.get(User, user_id)


def update_user_age(session, user_id: int, new_age: int) -> Optional[User]:
    u = session.get(User, user_id)
    if u is None:
        return None
    u.age = new_age
    session.add(u)
    session.commit()
    session.refresh(u)
    return u


def delete_user(session, user_id: int) -> bool:
    u = session.get(User, user_id)
    if u is None:
        return False
    session.delete(u)
    session.commit()
    return True


def list_users(session, limit: Optional[int] = None, offset: int = 0):
    """Return users with optional limit/offset."""
    q = session.query(User).order_by(User.id).offset(offset)
    if limit is not None:
        q = q.limit(limit)
    return q.all()


def paginate_users(session, page: int = 1, per_page: int = 10):
    """Simple pagination helper: returns (items, total, page, per_page)."""
    if page < 1:
        page = 1
    if per_page < 1:
        per_page = 10
    total = session.query(User).count()
    offset = (page - 1) * per_page
    items = list_users(session, limit=per_page, offset=offset)
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
    }


def filter_users_by_age(session, min_age: Optional[int] = None, max_age: Optional[int] = None):
    """Return users filtered by age range (inclusive).

    If `min_age`/`max_age` are None they are ignored.
    """
    q = session.query(User)
    if min_age is not None:
        q = q.filter(User.age >= min_age)
    if max_age is not None:
        q = q.filter(User.age <= max_age)
    return q.order_by(User.id).all()


def demo():
    """Small interactive demo that uses configured database (SQLite or PostgreSQL)."""
    from db_config import init_db

    engine, Session = init_db()
    session = Session()

    alice = create_user(session, 'Alice Demo', 28)
    print('Created:', alice.id, alice.name, alice.age)

    u = get_user(session, alice.id)
    print('Fetched:', u.id, u.name, u.age)

    update_user_age(session, alice.id, 29)
    print('Updated age to 29')

    delete_user(session, alice.id)
    print('Deleted user')

    # Demonstrate list, filter and pagination
    # Create sample rows
    create_user(session, 'User1', 20)
    create_user(session, 'User2', 25)
    create_user(session, 'User3', 30)

    print('All users:', [
          f"{u.id}:{u.name}({u.age})" for u in list_users(session)])
    print('Filtered (age>=25):', [
          u.name for u in filter_users_by_age(session, min_age=25)])
    pag = paginate_users(session, page=1, per_page=2)
    print('Page 1 items:', [
          u.name for u in pag['items']], 'total:', pag['total'])

    session.close()


def cli():
    import argparse
    from db_config import init_db

    parser = argparse.ArgumentParser(description='CRUD demo and helpers')
    sub = parser.add_subparsers(dest='cmd')

    # create
    p_create = sub.add_parser('create')
    p_create.add_argument('name')
    p_create.add_argument('--age', type=int, default=None)

    # get
    p_get = sub.add_parser('get')
    p_get.add_argument('id', type=int)

    # update
    p_update = sub.add_parser('update')
    p_update.add_argument('id', type=int)
    p_update.add_argument('--age', type=int, required=True)

    # delete
    p_delete = sub.add_parser('delete')
    p_delete.add_argument('id', type=int)

    # list
    p_list = sub.add_parser('list')
    p_list.add_argument('--limit', type=int, default=None)
    p_list.add_argument('--offset', type=int, default=0)

    # paginate
    p_pag = sub.add_parser('paginate')
    p_pag.add_argument('--page', type=int, default=1)
    p_pag.add_argument('--per-page', type=int, dest='per_page', default=10)

    # filter
    p_filt = sub.add_parser('filter')
    p_filt.add_argument('--min-age', type=int, default=None)
    p_filt.add_argument('--max-age', type=int, default=None)

    # demo
    sub.add_parser('demo')

    args = parser.parse_args()

    # Initialize database (uses DATABASE_URL env var or SQLite by default)
    engine, Session = init_db()
    session = Session()

    try:
        if args.cmd == 'create':
            u = create_user(session, args.name, args.age)
            print(f'Created: {u.id} {u.name} ({u.age})')
        elif args.cmd == 'get':
            u = get_user(session, args.id)
            if u:
                print(f'{u.id}: {u.name} ({u.age})')
            else:
                print('Not found')
        elif args.cmd == 'update':
            u = update_user_age(session, args.id, args.age)
            if u:
                print(f'Updated: {u.id} {u.name} ({u.age})')
            else:
                print('Not found')
        elif args.cmd == 'delete':
            ok = delete_user(session, args.id)
            print('Deleted' if ok else 'Not found')
        elif args.cmd == 'list':
            users = list_users(session, limit=args.limit, offset=args.offset)
            for u in users:
                print(f'{u.id}: {u.name} ({u.age})')
        elif args.cmd == 'paginate':
            pag = paginate_users(session, page=args.page,
                                 per_page=args.per_page)
            print(
                f"Page {pag['page']} ({pag['per_page']} per page) - total: {pag['total']}")
            for u in pag['items']:
                print(f'{u.id}: {u.name} ({u.age})')
        elif args.cmd == 'filter':
            users = filter_users_by_age(
                session, min_age=args.min_age, max_age=args.max_age)
            for u in users:
                print(f'{u.id}: {u.name} ({u.age})')
        elif args.cmd == 'demo' or args.cmd is None:
            demo()
        else:
            parser.print_help()
    finally:
        session.close()


if __name__ == '__main__':
    cli()
