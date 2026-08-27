import allure
import pytest
import requests
import random

from data import BASE_URL, TEST_USER, ORDER_INGREDIENTS
from api_client import register_user, login_user, create_order, get_ingredients


@allure.feature('Создание пользователя')
class TestCreateUser:

    @allure.title('Создание уникального пользователя')
    def test_create_unique_user(self, create_user, delete_user_after_test):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        
        response = register_user(email, TEST_USER['password'], TEST_USER['name'])
        
        access_token = response.json().get('accessToken')
        if access_token:
            delete_user_after_test.append(access_token)
        
        assert response.status_code == 200
        assert response.json()['success'] is True

    @allure.title('Создание пользователя, который уже зарегистрирован')
    def test_create_existing_user(self, create_user):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        
        create_user(email, TEST_USER['password'], TEST_USER['name'])
        response = create_user(email, TEST_USER['password'], TEST_USER['name'])
        
        assert response.status_code == 403
        assert response.json()['message'] == 'User already exists'

    @allure.title('Создание пользователя без одного из обязательных полей')
    @pytest.mark.parametrize('missing_field', ['email', 'password', 'name'])
    def test_create_user_missing_field(self, missing_field):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        payload = {
            'email': email,
            'password': TEST_USER['password'],
            'name': TEST_USER['name']
        }
        del payload[missing_field]
        
        response = requests.post(f'{BASE_URL}/auth/register', json=payload)
        
        assert response.status_code == 403
        assert response.json()['message'] == 'Email, password and name are required fields'


@allure.feature('Логин пользователя')
class TestLoginUser:

    @allure.title('Логин под существующим пользователем')
    def test_login_existing_user(self, create_user, delete_user_after_test):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        password = TEST_USER['password']
        
        create_user(email, password, TEST_USER['name'])
        
        response = login_user(email, password)
        
        access_token = response.json().get('accessToken')
        if access_token:
            delete_user_after_test.append(access_token)
        
        assert response.status_code == 200
        assert response.json()['success'] is True

    @allure.title('Логин с неверным логином и паролем')
    def test_login_invalid_credentials(self):
        payload = {'email': 'wrong@yandex.ru', 'password': 'wrongpassword'}
        response = requests.post(f'{BASE_URL}/auth/login', json=payload)
        
        assert response.status_code == 401
        assert response.json()['message'] == 'email or password are incorrect'


@allure.feature('Создание заказа')
class TestCreateOrder:

    @allure.title('Создание заказа с авторизацией')
    def test_create_order_with_auth(self, create_user, delete_user_after_test):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        response = create_user(email, TEST_USER['password'], TEST_USER['name'])
        access_token = response.json().get('accessToken')
        if access_token:
            delete_user_after_test.append(access_token)
        
        ingredient_ids = get_ingredients()
        response = create_order(ingredient_ids, access_token)
        
        assert response.status_code == 200
        assert response.json()['success'] is True

    @allure.title('Создание заказа без авторизации')
    def test_create_order_without_auth(self):
        ingredient_ids = get_ingredients()
        response = create_order(ingredient_ids)
        
        assert response.status_code == 200
        assert response.json()['success'] is True

    @allure.title('Создание заказа с ингредиентами')
    def test_create_order_with_ingredients(self, create_user, delete_user_after_test):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        response = create_user(email, TEST_USER['password'], TEST_USER['name'])
        access_token = response.json().get('accessToken')
        if access_token:
            delete_user_after_test.append(access_token)
        
        ingredient_ids = get_ingredients()
        response = create_order(ingredient_ids, access_token)
        
        assert response.status_code == 200
        assert len(response.json()['order']['ingredients']) == 2

    @allure.title('Создание заказа без ингредиентов')
    def test_create_order_no_ingredients(self, create_user, delete_user_after_test):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        response = create_user(email, TEST_USER['password'], TEST_USER['name'])
        access_token = response.json().get('accessToken')
        if access_token:
            delete_user_after_test.append(access_token)
        
        response = create_order([], access_token)
        
        assert response.status_code == 400
        assert response.json()['message'] == 'Ingredient ids must be provided'

    @allure.title('Создание заказа с неверным хешем ингредиентов')
    def test_create_order_invalid_ingredient_hash(self, create_user, delete_user_after_test):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        response = create_user(email, TEST_USER['password'], TEST_USER['name'])
        access_token = response.json().get('accessToken')
        if access_token:
            delete_user_after_test.append(access_token)
        
        response = create_order(['invalid_hash_1', 'invalid_hash_2'], access_token)
        
        assert response.status_code == 500