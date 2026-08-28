import pytest
import requests
from data import BASE_URL


@pytest.fixture
def create_user():
    """Фикстура для создания пользователя"""
    def _create_user(email, password, name):
        payload = {
            'email': email,
            'password': password,
            'name': name
        }
        response = requests.post(f'{BASE_URL}/auth/register', json=payload)
        return response
    return _create_user


@pytest.fixture
def delete_user():
    """Фикстура для удаления пользователя по токену"""
    def _delete_user(access_token):
        if access_token:
            headers = {'Authorization': access_token}
            requests.delete(f'{BASE_URL}/auth/user', headers=headers)
    return _delete_user


@pytest.fixture
def delete_user_after_test(delete_user):
    """Фикстура для удаления пользователя после теста"""
    tokens = []
    yield tokens
    for token in tokens:
        delete_user(token)