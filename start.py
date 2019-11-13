import os
from sys import exit
from functions import get_data_from_api

users_api_url = 'https://jsonplaceholder.typicode.com/users'
todos_api_url = 'https://jsonplaceholder.typicode.com/todos'

if __name__ == '__main__':
    # Получаем данные от api
    try:
        users_data = get_data_from_api(users_api_url)
        todos_data = get_data_from_api(todos_api_url)
    except Exception as e:
        print(e)
        input('Для завершения работы нажмите Enter...')
        exit(0)

    # Если каталог с отчетами не существует - создаем его
    if not os.path.isdir('tasks'):
        os.mkdir('tasks')
