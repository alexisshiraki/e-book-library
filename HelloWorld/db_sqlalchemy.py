"""Small SQLAlchemy ORM example using SQLite.

Creates a `users` table, inserts a row, and prints all rows.
"""
from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    age = Column(Integer)


def main():
    engine = create_engine('sqlite:///data.db', echo=False, future=True)
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine, future=True)
    session = Session()

    # Insert example row
    alice = User(name='Alice', age=30)
    session.add(alice)
    session.commit()

    # Query and print
    users = session.query(User).all()
    for u in users:
        print(f"{u.id}: {u.name} ({u.age})")

    session.close()


if __name__ == '__main__':
    main()
