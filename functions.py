import requests


# Функция получает от api объет json с требуемыми данными.
# Если получить объект не удалось - возбуждает исключение.
def get_data_from_api(api_url):
    request = requests.get(api_url)
    status_code = request.status_code
    if status_code != 200:
        raise Exception('Не удалось получить данные от api. Код ошибки: ' + str(status_code))
    return request.json()
