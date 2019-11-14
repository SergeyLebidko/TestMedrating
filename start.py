import os
import requests
from datetime import datetime
from sys import exit

# Основные параметры работы программы: адреса api-интерфейсов и наименование папки с отчетами
USERS_API_URL = 'https://jsonplaceholder.typicode.com/users'
TASKS_API_URL = 'https://jsonplaceholder.typicode.com/todos'
REPORT_FOLDER = 'tasks'


def get_data_from_api(api_url):
    """
    Функция получает данные от api.
    Если во время получения данных произошла ошибка, то возбуждается исключение.
    :param api_url: адрес api-интерфейса
    :return: полученные от api данные
    """
    request = requests.get(api_url)
    status_code = request.status_code
    if status_code != 200:
        raise Exception('Не удалось получить данные от api. Http-код ошибки: ' + str(status_code))
    return request.json()


def get_user_tasks(tasks_list, user_id, completed):
    """
    Функция формирует и возвращает список с наименованиями задач пользователя
    :param tasks_list: словарь json с данными о задачах
    :param user_id: пользователь, данные о котором надо извлечь из словаря задач
    :param completed: признак завершения задач (если True, извлекаем завершенные задачи;
                      если False - извлекаем незавершенные задачи)
    :return: список с наименованиями задач, удовлетворяющих условиям фильтрации
    """
    result = []
    for task in tasks_list:
        if task['userId'] == user_id and task['completed'] == completed:
            task_name = task['title']
            if len(task_name) > 50:
                task_name = task_name[:50] + '...'
            result.append(task_name)

    return result


def check_and_create_report_folder():
    """Функция проверяет наличие папки с отчетами и если её нет - создаёт её"""
    if not os.path.isdir(REPORT_FOLDER):
        os.mkdir(REPORT_FOLDER)


def check_and_rename_old_file(username):
    """
    Функция ищет на диске файл с отчетом по пользователю
    Если такой файл есть - переименовывает его, добавляя к имени дату формирования отчета из самого файла
    :param username: имя пользователя, по которому проверяем наличие отчета на диске
    """
    file_path = REPORT_FOLDER + '/' + username + '.txt'
    # Если отчет существует, то...
    if os.path.exists(file_path):
        # ...читаем первую строку файла с отчетом...
        file = open(REPORT_FOLDER + '/' + username + '.txt', 'r')
        first_line = file.readline()
        file.close()

        # ...и извлекаем из неё дату создания отчета и...
        date_created = first_line[first_line.index('>') + 2:len(first_line) - 1]
        date_created = date_created.replace(' ', 'T').replace('.', '-').replace(':', '-')

        # ...переименовываем найденный файл
        # При этом при переименовании нужно учитывать тот факт, что при слишком частых запросах к api
        # могут создаваться файлы с одинаковым временем создания отчета и это будет приводить к ошибке FileExistsError.
        # В случае возникновения этой ошибки я решил к концу каждого имени файла добавлять его порядковый номер
        # О возможности возникновения этой ошибки не было сказано в задании, я нашел её сам в ходе тестирования
        number = 0
        while True:
            number_str = '(' + str(number) + ')' if number > 0 else ''
            try:
                new_file_path = REPORT_FOLDER + '/' + username + '_' + date_created + number_str + '.txt'
                os.rename(file_path, new_file_path)
                break
            except FileExistsError:
                number += 1


def write_data_to_tmp_file(username, data):
    """
    Функция записывает переданный ей отчет во временный файл
    :param username: пользователь, данные по которому будем записывать в файл
    :param data: список строк, для записи в файл
    """
    file_path = REPORT_FOLDER + '/tmp_' + username + '.txt'
    try:
        file = open(file_path, 'w')
        for data_element in data:
            file.write(data_element + '\n')
        file.close()
    except Exception as e:
        os.remove(file_path)
        raise Exception('Не удалось сохранить отчет по пользователю: ' + username + ' Ошибка: ' + str(e))


def rename_tmp_file(username):
    """
    Функция переименовывает временный файл с отчетом по пользователю
    :param username: имя пользователя для формирования пути к файлу
    :return: None
    """
    old_file_path = REPORT_FOLDER + '/tmp_' + username + '.txt'
    new_file_path = REPORT_FOLDER + '/' + username + '.txt'
    os.rename(old_file_path, new_file_path)


if __name__ == '__main__':
    print('Начинаем...')

    # Получаем данные от api
    try:
        users_data = get_data_from_api(USERS_API_URL)
        tasks_data = get_data_from_api(TASKS_API_URL)
        print('Данные от api успешно получены')
    except Exception as e:
        # Если возникла ошибка при получении данных от api - выводим сообщение об ошибке и завершаем работу
        print(e)
        input('Для завершения работы нажмите Enter...')
        exit(0)

    # Проверяем наличие каталога с отчетами. Если его нет - он будет создан
    check_and_create_report_folder()

    # В цикле перебираем пользователей
    for user in users_data:
        # Список строк, которые будут записаны в файл
        file_data = []

        # Готовим первую строку с информацией о пользователе
        user_info = user['name']

        # Предусматриваем случай, если у пользователя нет адреса электронной почты
        if 'email' in user:
            user_info += '<' + user['email'] + '>'
        else:
            user_info += '<email отсутствует>'

        # Добавляем дату формирования отчета
        user_info += ' ' + datetime.today().strftime('%d.%m.%Y %H:%M')
        file_data.append(user_info)

        # Готовим вторую строку - с названием компании
        # Также предусматриваем особый случай (хотя он и кажется мне маловероятным), если у пользователя нет компании
        if 'company' in user:
            company_info = user['company']['name']
        else:
            company_info = ' - компания не найдена'
        file_data.append(company_info)

        # Добавляем данные о завершенных и незавершенных задачах пользователя
        tasks_description = [('Завершенные задачи:', True), ('Оставшиеся задачи:', False)]
        for description, completed_flag in tasks_description:
            file_data.append('')
            file_data.append(description)
            user_tasks = get_user_tasks(tasks_data, user['id'], completed_flag)
            if user_tasks:
                for task in user_tasks:
                    file_data.append(task)
            else:
                # Предусматриваем особый случай: задач (завершенных или незавершенных) нет
                file_data.append(' - таких задач нет')

        # Как только отчет по пользователю сформирован в оперативной памяти - начинаем выполнять файловые операции:
        #  - сперва записываем отчет во временный файл
        #  - если запись прошла успешно, то переименовываем старый файл с отчетом по пользователю (если он есть)
        #  - если же при записи произошел сбой, то временный файл просто удаляем и выводим сообщение об ошибке в консоль
        #  - последний этап - переименовываем временный файл со свежим отчетом
        # Таким образом, на диске в любом случае будет существовать отчет без даты в названии
        try:
            write_data_to_tmp_file(user['username'], file_data)
            check_and_rename_old_file(user['username'])
            rename_tmp_file(user['username'])
        except Exception as e:
            print(e)

    print('Работа завершена. Для выхода нажмите Enter...')
    input()
