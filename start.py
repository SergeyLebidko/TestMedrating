import os
import requests
from datetime import datetime
from sys import exit

USERS_API_URL = 'https://jsonplaceholder.typicode.com/users'
TASKS_API_URL = 'https://jsonplaceholder.typicode.com/todos'


def get_data_from_api(api_url):
    """
    :param api_url: адрес api-интерфейса
    :return: полученные от api данные
    """
    request = requests.get(api_url)
    status_code = request.status_code
    if status_code != 200:
        raise Exception('Не удалось получить данные от api. Код ошибки: ' + str(status_code))
    return request.json()


def get_user_tasks(tasks_list, user_id, completed):
    """
    :param tasks_list: словарь json с данными о задачах
    :param user_id: пользователь, данные о котором надо извлечь из словаря
    :param completed: признак завершения задач (если True, извлекаем завершенные задачи;
                      если False - извлекаем не завершенные задачи)
    :return: наименования задач, удовлетворяющих условиям фильтрации
    """
    result = []
    for task in tasks_list:
        if task['userId'] == user_id and task['completed'] == completed:
            task_name = task['title']
            if len(task_name) > 50:
                task_name = task_name[:50] + '...'
            result.append(task_name)

    return result


if __name__ == '__main__':
    # Получаем данные от api
    try:
        users_data = get_data_from_api(USERS_API_URL)
        tasks_data = get_data_from_api(TASKS_API_URL)
    except Exception as e:
        # Если возникла ошибка при получении данных от api - выводим сообщение об ошибке и завершаем работу
        print(e)
        input('Для завершения работы нажмите Enter...')
        exit(0)

    # Если каталог с отчетами не существует - создаем его
    if not os.path.isdir('tasks'):
        os.mkdir('tasks')

    # В цикле перебираем пользователей
    for user in users_data:
        # Фомируем имя файла, соответствующее текущему пользователю
        filename = 'tasks/' + user['username']

        # Проверяем, существует ли такой файл
        # И если существует, то переименовываем его и только потом записываем новый файл
        if os.path.exists(filename + '.txt'):
            # Читаем первую строку файла с отчетом...
            file = open(filename + '.txt', 'r')
            first_line = file.readline()
            file.close()

            # ...и извлекаем из неё дату создания отчета
            date_created = first_line[first_line.index('>') + 2:len(first_line) - 1]
            date_created = date_created.replace(' ', 'T')
            date_created = date_created.replace('.', '-')
            date_created = date_created.replace(':', '-')

            # Переименовываем файл
            os.rename(filename + '.txt', filename + '_' + date_created + '.txt')

        # Записываем новый файл
        file = open(filename + '.txt', 'w')

        # Готовим первую строку с информацией о пользователе
        user_info = user['name']

        # Предусматриваем случай, если у пользователя нет адреса электронной почты
        if 'mail' in user:
            user_info += '<' + user['email'] + '>'
        else:
            user_info += '<email отсутствует>'

        # Добавляем дату формирования отчета
        user_info += ' ' + datetime.today().strftime('%d.%m.%Y %H:%M')

        # Готовим вторую строку с названием компании
        # Также предусматриваем особый случай (хотя он и кажется мне маловероятным), если у пользователя нет компании
        if 'company' in user:
            company_info = user['company']['name']
        else:
            company_info = ' - компания, не найдена'

        # Записываем в файл данные о пользователе и названии компании
        file.write(user_info + '\n')
        file.write(company_info + '\n')

        # Записываем в файл данные о завершенных и незавершенных задачах пользователя
        tasks_description = [('Завершенные задачи:', True), ('Оставшиеся задачи:', False)]
        for description, completed_flag in tasks_description:
            file.write('\n')
            file.write(description + '\n')
            user_tasks = get_user_tasks(tasks_data, user['id'], completed_flag)
            if user_tasks:
                for task in user_tasks:
                    file.write(task + '\n')
            else:
                # Предусматриваем особый случай: задач (завершенных или незавершенных) нет
                file.write(' - таких задач нет\n')

        # Закрываем файл
        file.close()
