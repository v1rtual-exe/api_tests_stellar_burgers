import pytest
import requests
import allure


class TestApi:

    @allure.title('Создание уникального пользователя')
    def test_create_unique_user(self, base_url):
        import random
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        payload = {
            'email': email,
            'password': 'password123',
            'name': 'TestUser'
        }
        response = requests.post(f'{base_url}/auth/register', json=payload)
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert response.json()['user']['email'] == email
        assert response.json()['user']['name'] == 'TestUser'
        assert 'accessToken' in response.json()

    @allure.title('Создание пользователя, который уже зарегистрирован')
    def test_create_existing_user(self, base_url):
        import random
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        payload = {
            'email': email,
            'password': 'password123',
            'name': 'TestUser'
        }
        requests.post(f'{base_url}/auth/register', json=payload)
        response = requests.post(f'{base_url}/auth/register', json=payload)
        assert response.status_code == 403
        assert response.json()['success'] is False
        assert response.json()['message'] == 'User already exists'

    @allure.title('Создание пользователя без одного из обязательных полей')
    @pytest.mark.parametrize('missing_field', ['email', 'password', 'name'])
    def test_create_user_missing_field(self, base_url, missing_field):
        import random
        payload = {
            'email': f'test_{random.randint(1000, 9999)}@yandex.ru',
            'password': 'password123',
            'name': 'TestUser'
        }
        del payload[missing_field]
        response = requests.post(f'{base_url}/auth/register', json=payload)
        assert response.status_code == 403
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Email, password and name are required fields'

    @allure.title('Логин под существующим пользователем')
    def test_login_existing_user(self, base_url):
        import random
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        password = 'password123'
        payload = {
            'email': email,
            'password': password,
            'name': 'TestUser'
        }
        requests.post(f'{base_url}/auth/register', json=payload)
        login_payload = {
            'email': email,
            'password': password
        }
        response = requests.post(f'{base_url}/auth/login', json=login_payload)
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert response.json()['user']['email'] == email
        assert 'accessToken' in response.json()

    @allure.title('Логин с неверным логином и паролем')
    def test_login_invalid_credentials(self, base_url):
        payload = {
            'email': 'wrong@yandex.ru',
            'password': 'wrongpassword'
        }
        response = requests.post(f'{base_url}/auth/login', json=payload)
        assert response.status_code == 401
        assert response.json()['success'] is False
        assert response.json()['message'] == 'email or password are incorrect'

    def get_ingredients(self, base_url):
        response = requests.get(f'{base_url}/ingredients')
        if response.status_code == 200:
            ingredients = response.json()['data']
            return [ingredient['_id'] for ingredient in ingredients[:2]]
        return ['60d3b41abdacab0026a733c6', '609646e4dc916e00276b2870']

    @allure.title('Создание заказа с авторизацией')
    def test_create_order_with_auth(self, base_url):
        import random
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        payload = {
            'email': email,
            'password': 'password123',
            'name': 'TestUser'
        }
        register_response = requests.post(f'{base_url}/auth/register', json=payload)
        access_token = register_response.json()['accessToken']
        headers = {'Authorization': access_token}
        ingredient_ids = self.get_ingredients(base_url)
        order_payload = {
            'ingredients': ingredient_ids
        }
        response = requests.post(f'{base_url}/orders', json=order_payload, headers=headers)
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert 'order' in response.json()
        assert 'number' in response.json()['order']

    @allure.title('Создание заказа без авторизации')
    def test_create_order_without_auth(self, base_url):
        ingredient_ids = self.get_ingredients(base_url)
        order_payload = {
            'ingredients': ingredient_ids
        }
        response = requests.post(f'{base_url}/orders', json=order_payload)
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert 'order' in response.json()

    @allure.title('Создание заказа с ингредиентами')
    def test_create_order_with_ingredients(self, base_url):
        import random
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        payload = {
            'email': email,
            'password': 'password123',
            'name': 'TestUser'
        }
        register_response = requests.post(f'{base_url}/auth/register', json=payload)
        access_token = register_response.json()['accessToken']
        headers = {'Authorization': access_token}
        ingredient_ids = self.get_ingredients(base_url)
        order_payload = {
            'ingredients': ingredient_ids
        }
        response = requests.post(f'{base_url}/orders', json=order_payload, headers=headers)
        assert response.status_code == 200
        assert response.json()['success'] is True
        assert len(response.json()['order']['ingredients']) == 2

    @allure.title('Создание заказа без ингредиентов')
    def test_create_order_no_ingredients(self, base_url):
        import random
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        payload = {
            'email': email,
            'password': 'password123',
            'name': 'TestUser'
        }
        register_response = requests.post(f'{base_url}/auth/register', json=payload)
        access_token = register_response.json()['accessToken']
        headers = {'Authorization': access_token}
        order_payload = {
            'ingredients': []
        }
        response = requests.post(f'{base_url}/orders', json=order_payload, headers=headers)
        assert response.status_code == 400
        assert response.json()['success'] is False
        assert response.json()['message'] == 'Ingredient ids must be provided'

    @allure.title('Создание заказа с неверным хешем ингредиентов')
    def test_create_order_invalid_ingredient_hash(self, base_url):
        import random
        email = f'test_{random.randint(1000, 9999)}@yandex.ru'
        payload = {
            'email': email,
            'password': 'password123',
            'name': 'TestUser'
        }
        register_response = requests.post(f'{base_url}/auth/register', json=payload)
        access_token = register_response.json()['accessToken']
        headers = {'Authorization': access_token}
        order_payload = {
            'ingredients': ['invalid_hash_1', 'invalid_hash_2']
        }
        response = requests.post(f'{base_url}/orders', json=order_payload, headers=headers)
        assert response.status_code == 500