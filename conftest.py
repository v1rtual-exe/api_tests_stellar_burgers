import pytest
import requests


@pytest.fixture
def base_url():
    return 'https://stellarburgers.education-services.ru/api'


@pytest.fixture
def create_user(base_url):
    def _create_user(email, password, name):
        payload = {
            'email': email,
            'password': password,
            'name': name
        }
        response = requests.post(f'{base_url}/auth/register', json=payload)
        return response
    return _create_user


@pytest.fixture
def delete_user(base_url):
    def _delete_user(access_token):
        headers = {'Authorization': access_token}
        requests.delete(f'{base_url}/auth/user', headers=headers)
    return _delete_user