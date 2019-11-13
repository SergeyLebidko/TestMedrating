import requests


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


def get_user_tasks(tasks_data, user_id, completed):
    """
    :param tasks_data: словарь json с данными о задачах
    :param user_id: пользователь, данные о котором надо извлечь из словаря
    :param completed: признак завершения задач (если True, извлекаем завершенные задачи;
                      если False - извлекаем не завершенные задачи)
    :return: наименования задач, удовлетворяющих условиям фильтрации
    """
    result = []
    for task in tasks_data:
        if task['userId'] == user_id and task['completed'] == completed:
            task_name = task['title']
            if len(task_name) > 50:
                task_name = task_name[:50] + '...'
            result.append(task_name)

    return result
