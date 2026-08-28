import allure
import requests
from data import BASE_URL


@allure.step('Регистрация пользователя')
def register_user(email, password, name):
    payload = {'email': email, 'password': password, 'name': name}
    return requests.post(f'{BASE_URL}/auth/register', json=payload)


@allure.step('Логин пользователя')
def login_user(email, password):
    payload = {'email': email, 'password': password}
    return requests.post(f'{BASE_URL}/auth/login', json=payload)


@allure.step('Создание заказа')
def create_order(ingredients, token=None):
    headers = {'Authorization': token} if token else {}
    payload = {'ingredients': ingredients}
    return requests.post(f'{BASE_URL}/orders', json=payload, headers=headers)


@allure.step('Получение ингредиентов')
def get_ingredients():
    response = requests.get(f'{BASE_URL}/ingredients')
    if response.status_code == 200:
        ingredients = response.json()['data']
        return [ingredient['_id'] for ingredient in ingredients[:2]]
    return []