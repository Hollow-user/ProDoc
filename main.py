import datetime
import os

import requests

api_url_todos = 'https://json.medrating.org/todos'
api_url_users = 'https://json.medrating.org/users'
folder_name = 'tasks'
current_time = datetime.datetime.now()


def get_data(url: str) -> list:
    """
    Получение данных через API
    :param url: ссылка
    :return: список словарей с данными
    """
    try:
        response = requests.get(url)
    except ConnectionError:
        raise Exception('Произошла ошибка сети, проверье соединение и попробуйте еще раз')
    except Exception as e:
        raise Exception(f'Произошла ошибка: {e}')
    else:
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f'Произошла ошибка при запросе, статус код: {response.status_code}')


def create_folder(path: str):
    """
    Создание папки
    :param path: путь до папки
    """
    if not os.path.exists(path):
        os.mkdir(path)


def check_user_file(username: str):
    """
    Проверка наличия последнего отчета по пользователю
    :param username: имя пользователя
    """
    file_path = f'{folder_name}/{username}.txt'
    time = current_time.strftime('%Y-%m-%dT%H:%M')
    if os.path.exists(file_path):
        os.rename(file_path, f'{folder_name}/{username}_{time}.txt')


def generate_todo(user_id: int, todos: list) -> str:
    """
    Генерация акутального списка задач
    :param user_id: id пользователя
    :param todos: список задач
    :return: актуальный список задач для отчета
    """
    complete_todos = 'Завершенные задачи:\n'
    uncomplete_todos = 'Оставшиеся задачи:\n'

    for todo in todos:
        try:
            if todo['userId'] == user_id:
                task_name = (todo['title'][:50]) if len(todo['title']) > 50 else todo['title']

                if todo['completed']:
                    complete_todos += task_name + '\n'
                else:
                    uncomplete_todos += task_name + '\n'
                todos.remove(todo)
        except KeyError:
            print(f'Не удалось распознать задачу: {todo}')
        except Exception as e:
            print(f'Произошла ошибка: {e}')

    if complete_todos == 'Завершенные задачи:\n':
        complete_todos += 'У пользователя нет завершенных задач\n'
    if uncomplete_todos == 'Оставшиеся задачи:\n':
        uncomplete_todos += 'У пользователя не осталось задач\n'

    return complete_todos + '\n' + uncomplete_todos


def create_file(username: str, user_id: int, name: str, email: str, company: str, todos: list):
    """
    Создание и запись данных о пользователе в файл
    :param username: имя пользователя
    :param user_id: id пользователя
    :param name: имя
    :param email: почта
    :param company: компания
    :param todos: задачи
    """
    time = current_time.strftime('%d.%m.%Y %H:%M')
    user_info = f'{name}<{email}> {time}\n' \
                f'{company}\n\n' \
                + generate_todo(user_id, todos)
    check_user_file(username)
    try:
        with open(f'{folder_name}/{username}.txt', 'w', encoding='utf-8') as file:
            file.write(user_info)
    except Exception as e:
        print(f'Произошла ошибка: {e}')


def generate_reports():
    """
    Генерация отчетов о пользователях
    """
    todos = get_data(api_url_todos)
    users = get_data(api_url_users)
    create_folder(folder_name)

    for user in users:
        try:
            username = user['username']
            user_id = user['id']
            name = user['name']
            email = user['email']
            company = user['company']['name']
        except KeyError:
            print(f'Не удалось распознать пользователя: {user}')
        except Exception as e:
            print(f'Произошла ошибка: {e}')
        else:
            create_file(username=username,
                        user_id=user_id,
                        name=name,
                        email=email,
                        company=company,
                        todos=todos)


if __name__ == '__main__':
    print('Начало работы скрипта')
    generate_reports()
    print('Работа закончена')
