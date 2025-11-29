"""Integration tests for PostgreSQL and SQLite databases.

Run with: pytest tests/test_integration.py -v

To test with PostgreSQL:
    DATABASE_URL="postgresql://user:pass@localhost:5432/test_db" pytest tests/test_integration.py -v

Expects a test database to exist:
    createdb test_db
"""
import os
import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from db_sqlalchemy import Base, User
from db_config import get_engine, init_db, drop_all
from crud import create_user, get_user, list_users, delete_user, update_user_age


@pytest.fixture(scope='module')
def test_db_url():
    """Get test database URL from environment or use SQLite.
    
    For PostgreSQL testing:
        Set DATABASE_URL="postgresql://user:pass@localhost:5432/test_db"
        Ensure database exists: createdb test_db
    """
    url = os.getenv('DATABASE_URL')
    
    # Use in-memory SQLite for default testing (fast, no setup)
    if url is None or not url.startswith(('postgresql://', 'postgres://')):
        return 'sqlite:///:memory:'
    
    # Use PostgreSQL test database if configured
    return url


@pytest.fixture(scope='module')
def module_engine(test_db_url):
    """Create a module-scoped engine for test database."""
    engine = get_engine(test_db_url)
    
    # Drop and recreate schema for clean state
    drop_all(test_db_url)
    Base.metadata.create_all(engine)
    
    yield engine
    
    # Cleanup: drop all tables after tests
    drop_all(test_db_url)


@pytest.fixture
def db_session(module_engine):
    """Provide a transactional session for each test.
    
    Uses SAVEPOINT pattern for isolation (works with SQLite and PostgreSQL).
    """
    connection = module_engine.connect()
    transaction = connection.begin()
    
    Session = sessionmaker(bind=connection, future=True)
    session = Session()
    
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


class TestSQLiteAndPostgres:
    """Test CRUD operations on both SQLite and PostgreSQL."""
    
    def test_create_user(self, db_session):
        """Test creating a user."""
        user = create_user(db_session, 'Alice', 30)
        assert user.id is not None
        assert user.name == 'Alice'
        assert user.age == 30
    
    def test_get_user(self, db_session):
        """Test retrieving a user."""
        user = create_user(db_session, 'Bob', 25)
        retrieved = get_user(db_session, user.id)
        assert retrieved is not None
        assert retrieved.name == 'Bob'
        assert retrieved.age == 25
    
    def test_get_nonexistent_user(self, db_session):
        """Test retrieving a user that doesn't exist."""
        user = get_user(db_session, 9999)
        assert user is None
    
    def test_update_user_age(self, db_session):
        """Test updating a user's age."""
        user = create_user(db_session, 'Charlie', 28)
        original_id = user.id
        
        updated = update_user_age(db_session, user.id, 35)
        assert updated is not None
        assert updated.id == original_id
        assert updated.age == 35
    
    def test_delete_user(self, db_session):
        """Test deleting a user."""
        user = create_user(db_session, 'Diana', 32)
        user_id = user.id
        
        success = delete_user(db_session, user_id)
        assert success is True
        
        # Verify user is gone
        retrieved = get_user(db_session, user_id)
        assert retrieved is None
    
    def test_delete_nonexistent_user(self, db_session):
        """Test deleting a user that doesn't exist."""
        success = delete_user(db_session, 9999)
        assert success is False
    
    def test_list_users(self, db_session):
        """Test listing users."""
        create_user(db_session, 'User1', 20)
        create_user(db_session, 'User2', 25)
        create_user(db_session, 'User3', 30)
        
        users = list_users(db_session)
        assert len(users) == 3
        assert users[0].name == 'User1'
        assert users[1].name == 'User2'
        assert users[2].name == 'User3'
    
    def test_list_users_with_limit(self, db_session):
        """Test listing users with limit."""
        create_user(db_session, 'User1', 20)
        create_user(db_session, 'User2', 25)
        create_user(db_session, 'User3', 30)
        
        users = list_users(db_session, limit=2)
        assert len(users) == 2
    
    def test_list_users_with_offset(self, db_session):
        """Test listing users with offset."""
        create_user(db_session, 'User1', 20)
        create_user(db_session, 'User2', 25)
        create_user(db_session, 'User3', 30)
        
        users = list_users(db_session, offset=1)
        assert len(users) == 2
        assert users[0].name == 'User2'
    
    def test_multiple_operations(self, db_session):
        """Test a sequence of CRUD operations."""
        # Create
        user1 = create_user(db_session, 'Alice', 25)
        user2 = create_user(db_session, 'Bob', 30)
        
        # List
        users = list_users(db_session)
        assert len(users) == 2
        
        # Update
        updated = update_user_age(db_session, user1.id, 26)
        assert updated.age == 26
        
        # Get
        retrieved = get_user(db_session, user1.id)
        assert retrieved.age == 26
        
        # Delete
        delete_user(db_session, user2.id)
        users = list_users(db_session)
        assert len(users) == 1
        assert users[0].name == 'Alice'


class TestDatabaseConnection:
    """Test database connection and initialization."""
    
    def test_init_db_creates_tables(self, test_db_url):
        """Test that init_db creates the schema."""
        # Use a fresh URL
        url = test_db_url if test_db_url.startswith('sqlite:///:memory:') else test_db_url
        
        engine, Session = init_db(url)
        
        # Verify tables exist by creating a session and querying
        session = Session()
        try:
            # This should work if User table exists
            users = session.query(User).all()
            assert isinstance(users, list)
        finally:
            session.close()
    
    def test_engine_creation_sqlite(self):
        """Test engine creation for SQLite."""
        engine = get_engine('sqlite:///:memory:')
        assert engine is not None
        
        # Verify it's usable
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            assert result.scalar() == 1
    
    def test_engine_creation_postgresql(self):
        """Test engine creation for PostgreSQL (skipped if not available)."""
        postgres_url = os.getenv('TEST_POSTGRES_URL')
        
        if postgres_url is None:
            pytest.skip('TEST_POSTGRES_URL not set')
        
        engine = get_engine(postgres_url)
        assert engine is not None
        
        # Verify it's usable
        with engine.connect() as conn:
            result = conn.execute(text('SELECT 1'))
            assert result.scalar() == 1
