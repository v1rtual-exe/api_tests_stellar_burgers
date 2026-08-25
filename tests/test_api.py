import allure
import pytest
import requests
import random

from data import BASE_URL, TEST_USER, ORDER_INGREDIENTS


@allure.feature('Создание пользователя')
class TestCreateUser:

    @allure.step('Создание уникального пользователя')
    def test_create_unique_user(self, create_user, delete_user):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        payload = {
            'email': email,
            'password': TEST_USER['password'],
            'name': TEST_USER['name']
        }
        
        response = create_user(email, payload['password'], payload['name'])
        
        assert response.status_code == 200
        assert response.json()['success'] is True
        
        delete_user(response.json()['accessToken'])

    @allure.step('Создание пользователя, который уже зарегистрирован')
    def test_create_existing_user(self, create_user):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        payload = {
            'email': email,
            'password': TEST_USER['password'],
            'name': TEST_USER['name']
        }
        
        create_user(email, payload['password'], payload['name'])
        response = create_user(email, payload['password'], payload['name'])
        
        assert response.status_code == 403
        assert response.json()['message'] == 'User already exists'

    @allure.step('Создание пользователя без одного из обязательных полей')
    @pytest.mark.parametrize('missing_field', ['email', 'password', 'name'])
    def test_create_user_missing_field(self, create_user, missing_field):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        payload = {
            'email': email,
            'password': TEST_USER['password'],
            'name': TEST_USER['name']
        }
        del payload[missing_field]
        
        response = create_user(payload.get('email'), payload.get('password'), payload.get('name'))
        
        assert response.status_code == 403
        assert response.json()['message'] == 'Email, password and name are required fields'


@allure.feature('Логин пользователя')
class TestLoginUser:

    @allure.step('Логин под существующим пользователем')
    def test_login_existing_user(self, create_user, delete_user):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        password = TEST_USER['password']
        
        create_user(email, password, TEST_USER['name'])
        
        login_payload = {'email': email, 'password': password}
        response = requests.post(f'{BASE_URL}/auth/login', json=login_payload)
        
        assert response.status_code == 200
        assert response.json()['success'] is True
        
        delete_user(response.json()['accessToken'])

    @allure.step('Логин с неверным логином и паролем')
    def test_login_invalid_credentials(self):
        payload = {'email': 'wrong@yandex.ru', 'password': 'wrongpassword'}
        response = requests.post(f'{BASE_URL}/auth/login', json=payload)
        
        assert response.status_code == 401
        assert response.json()['message'] == 'email or password are incorrect'


@allure.feature('Создание заказа')
class TestCreateOrder:

    def get_ingredients(self):
        response = requests.get(f'{BASE_URL}/ingredients')
        if response.status_code == 200:
            ingredients = response.json()['data']
            return [ingredient['_id'] for ingredient in ingredients[:2]]
        return ORDER_INGREDIENTS

    @allure.step('Создание заказа с авторизацией')
    def test_create_order_with_auth(self, create_user, delete_user):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        response = create_user(email, TEST_USER['password'], TEST_USER['name'])
        access_token = response.json()['accessToken']
        headers = {'Authorization': access_token}
        
        ingredient_ids = self.get_ingredients()
        order_payload = {'ingredients': ingredient_ids}
        
        response = requests.post(f'{BASE_URL}/orders', json=order_payload, headers=headers)
        
        assert response.status_code == 200
        assert response.json()['success'] is True
        
        delete_user(access_token)

    @allure.step('Создание заказа без авторизации')
    def test_create_order_without_auth(self):
        ingredient_ids = self.get_ingredients()
        order_payload = {'ingredients': ingredient_ids}
        response = requests.post(f'{BASE_URL}/orders', json=order_payload)
        
        assert response.status_code == 200
        assert response.json()['success'] is True

    @allure.step('Создание заказа с ингредиентами')
    def test_create_order_with_ingredients(self, create_user, delete_user):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        response = create_user(email, TEST_USER['password'], TEST_USER['name'])
        access_token = response.json()['accessToken']
        headers = {'Authorization': access_token}
        
        ingredient_ids = self.get_ingredients()
        order_payload = {'ingredients': ingredient_ids}
        
        response = requests.post(f'{BASE_URL}/orders', json=order_payload, headers=headers)
        
        assert response.status_code == 200
        assert len(response.json()['order']['ingredients']) == 2
        
        delete_user(access_token)

    @allure.step('Создание заказа без ингредиентов')
    def test_create_order_no_ingredients(self, create_user, delete_user):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        response = create_user(email, TEST_USER['password'], TEST_USER['name'])
        access_token = response.json()['accessToken']
        headers = {'Authorization': access_token}
        
        order_payload = {'ingredients': []}
        response = requests.post(f'{BASE_URL}/orders', json=order_payload, headers=headers)
        
        assert response.status_code == 400
        assert response.json()['message'] == 'Ingredient ids must be provided'
        
        delete_user(access_token)

    @allure.step('Создание заказа с неверным хешем ингредиентов')
    def test_create_order_invalid_ingredient_hash(self, create_user, delete_user):
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        response = create_user(email, TEST_USER['password'], TEST_USER['name'])
        access_token = response.json()['accessToken']
        headers = {'Authorization': access_token}
        
        order_payload = {'ingredients': ['invalid_hash_1', 'invalid_hash_2']}
        response = requests.post(f'{BASE_URL}/orders', json=order_payload, headers=headers)
        
        assert response.status_code == 500
        
        delete_user(access_token)