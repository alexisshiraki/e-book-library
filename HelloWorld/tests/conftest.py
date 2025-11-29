import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db_sqlalchemy import Base
from db_sqlalchemy import User


@pytest.fixture(scope='session')
def engine():
    """Create a session-scoped in-memory SQLite engine and initialize schema."""
    engine = create_engine('sqlite:///:memory:', future=True)
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def session(engine):
    """Provide a transactional SQLAlchemy `Session` for each test.

    Uses a SAVEPOINT / nested transaction pattern: open a connection and
    begin a transaction, yield a session bound to that connection, and
    rollback the outer transaction at teardown so tests are isolated.
    """
    connection = engine.connect()
    transaction = connection.begin()

    Session = sessionmaker(bind=connection, future=True)
    sess = Session()

    try:
        yield sess
    finally:
        sess.close()
        # rollback the broader transaction, removing any test data
        transaction.rollback()
        connection.close()


@pytest.fixture
def db(session):
    """Provide a small helper API for tests to create sample rows.

    Usage:
        user = db.create_user(name='Alice', age=30)
        users = db.all_users()
    """
    class DBHelper:
        def create_user(self, name='User', age=20):
            u = User(name=name, age=age)
            session.add(u)
            session.commit()
            return u

        def all_users(self):
            return session.query(User).all()

        def clear(self):
            session.query(User).delete()
            session.commit()

    return DBHelper()
