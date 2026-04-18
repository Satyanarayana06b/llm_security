import pytest

from app.middleware.auth import (
    create_user,
    authenticate_user,
    fake_users_db,
    hash_password, 
    create_access_token
)

class TestAuth:

    def setup_method(self):
        fake_users_db.clear()

    def test_create_user(self):
        user = create_user("testuser", "password123")
        assert user["username"] == "testuser"
        assert "testuser" in fake_users_db

    def test_create_duplicate_user_fails(self):
        create_user("testuser", "password123")
        with pytest.raises(ValueError, match="already exists"):
            create_user("testuser", "newpassword")

    def test_authenticate_valid_user(self):
        create_user("testuser", "password123")
        user = authenticate_user("testuser", "password123")
        assert user is not None
        assert user["username"] == "testuser"

    def test_authenticate_wrong_password(self):
        create_user("testuser", "password123")
        user = authenticate_user("testuser", "wrongpassword")
        assert user is None
    
    def test_authenticate_nonexistent_user(self):
        user = authenticate_user("nonexistent", "password123")
        assert user is None

    def test_create_access_token(self):
        token = create_access_token("testuser")
        assert isinstance(token, str)
        assert len(token) > 20

    def test_hash_password_deterministic(self):
        h1 = hash_password("password123")
        h2 = hash_password("password123")
        assert h1 == h2

    def test_hash_password_different_inputs(self):
        h1 = hash_password("password123")
        h2 = hash_password("differentpassword")
        assert h1 != h2