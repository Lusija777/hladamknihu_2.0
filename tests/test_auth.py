import pytest
from flask import g, session
from flaskr.db import get_db


def test_register(runner, app):
    result = runner.invoke(args=['auth', 'create-user', 'a', 'a'])
    assert "User a created successfully." in result.output

    with app.app_context():
        assert get_db().execute(
            "SELECT * FROM user WHERE username = 'a'",
        ).fetchone() is not None


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('', '', 'Username is required.'),
    ('a', '', 'Password is required.'),
    ('test', 'test', 'User test is already registered.'),
))
def test_register_validate_input(runner, username, password, message):
    result = runner.invoke(args=['auth', 'create-user', username, password])
    assert message in result.stderr



def test_login(client, auth):
    assert client.get('/auth/login').status_code == 200
    response = auth.login()
    assert response.headers["Location"] == "/"

    with client:
        client.get('/')
        assert session['user_id'] == 1
        assert g.user['username'] == 'test'


@pytest.mark.parametrize(('username', 'password', 'message'), (
    ('a', 'test', b'Incorrect username.'),
    ('test', 'a', b'Incorrect password.'),
))
def test_login_validate_input(auth, username, password, message):
    response = auth.login(username, password)
    assert message in response.data

def test_logout(client, auth):
    auth.login()

    with client:
        auth.logout()
        assert 'user_id' not in session