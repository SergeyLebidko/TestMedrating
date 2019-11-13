import os
from datetime import datetime
from sys import exit
from functions import get_data_from_api, get_user_tasks

users_api_url = 'https://jsonplaceholder.typicode.com/users'
todos_api_url = 'https://jsonplaceholder.typicode.com/todos'

if __name__ == '__main__':
    # Получаем данные от api
    try:
        users_data = get_data_from_api(users_api_url)
        tasks_data = get_data_from_api(todos_api_url)
    except Exception as e:
        # Если возникла ошибка при получении данных от api - выводим сообщение об ошибке и завершаем работу
        print(e)
        input('Для завершения работы нажмите Enter...')
        exit(0)

    # Если каталог с отчетами не существует - создаем его
    if not os.path.isdir('tasks'):
        os.mkdir('tasks')

    # Во цикле перебираем пользователей
    for user in users_data:
        # Открываем файл, соответствующий пользователю, в режиме "запись"
        filename = 'tasks/' + user['username'] + '.txt'
        file = open(filename, 'w')

        # Готовим первую строку с информацией о пользователе
        user_info = user['name'] + '<' + user['email'] + '>' + ' ' + datetime.today().strftime('%d.%m.%Y %H:%M')

        # Готовим вторую строку с названием компании
        company_info = user['company']['name']

        # Записываем в файл данные о пользователе и названии компании
        file.write(user_info + '\n')
        file.write(company_info + '\n')
        file.write('\n')

        # Формируем список завешенных пользователем задач и записываем их в файл
        file.write('Завершенные задачи:\n')
        completed_tasks = get_user_tasks(tasks_data, user['id'], True)
        for task in completed_tasks:
            file.write(task + '\n')

        # Вставляем в файл пустую строку между списками задач
        file.write('\n')

        # Формируем список не завершенных задач и записываем их в файл
        file.write('Оставшиеся задачи:\n')
        not_completed_tasks = get_user_tasks(tasks_data, user['id'], False)
        for task in not_completed_tasks:
            file.write(task + '\n')

        # Закрываем файл
        file.close()
