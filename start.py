import os
from datetime import datetime
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

    # Во внешнем цикле перебираем пользователей
    for user in users_data:
        # Открываем файл, соответствующий пользователю, в режиме "запись"
        filename = 'tasks/' + user['username'] + '.txt'
        file = open(filename, 'w')

        # Готовим первую строку с информацией о пользователе
        user_info = user['name'] + '<' + user['email'] + '>' + ' ' + datetime.today().strftime('%d.%m.%Y %H:%M')

        # Готовим вторую строку с названием компании
        company_info = user['company']['name']

        file.write(user_info+'\n')
        file.write(company_info+'\n')
        file.write('\n')
        file.write('Завершенные задачи:\n')
        file.write('--- список завершенных задач\n')
        file.write('\n')
        file.write('Оставшиеся задачи:\n')
        file.write('--- список оставшихся задач\n')

        # Закрываем файл
        file.close()
