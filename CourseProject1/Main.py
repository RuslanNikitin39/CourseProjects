import os
from builtins import sorted, type
import requests
import json
from pprint import pprint
import yadisk
from ya_disk import YandexDisk
import time
from datetime import datetime
from progress.bar import IncrementalBar

def _get_settings():
    """ Формат записей настроек см. в файле token1.txt"""
    path = os.path.join(os.getcwd(), 'token.txt')
    t_dict = {}
    if os.path.isfile(path):
        with open(path, 'r') as file_object:
            for item in file_object:
                token_name, token = item.strip().split(':')
                t_dict[token_name] = token
    else:
        print(f'Настройки не найдены.\n')
        t_dict['ya_token'] = input(f'Введите токен для Yandex: ')
        t_dict['vk_user_id'] = input(f'Введите USER_ID для VK: ')
        t_dict['vk_token'] = input(f'Введите токен для VK: ')

    return t_dict

def get_photo_data(vk_user_id, vk_token):
    """ Получим фото с профиля"""
    api = requests.get("https://api.vk.com/method/photos.get", params={
        'owner_id' : vk_user_id,
        'access_token' : vk_token,
        'album_id': 'profile' ,
        # 'album_id' : '281897303',
        'extended' : 1,
        'offset' : 0,
        'photo_size' : 0,
        'v' : 5.103
    })
    if api.status_code == 200:
        return api.json()
    else:
        return api.status_code

def get_photo_name(photo_name, photo_date, result_dict):
    """Нужна уникальность, есть фото без лайков, залитые в одно время,
    поэтому добавим префикс
    """
    prefix = 0
    new_photo_name = photo_name
    while not result_dict.get(new_photo_name) == None:
        if not photo_date == 0:
            photo_name = f'{photo_date}_{photo_name}'
            new_photo_name = photo_name
            photo_date = 0
        else:
            prefix += 1
            new_photo_name = f'{prefix}_{photo_name}'

    return new_photo_name


if __name__ == '__main__':
    print(f'Поиск файла настроек.\n')
    settings = _get_settings()
    print(f'Настройки получены. Запрашиваю данные.\n')
    # albums = get_photo_albums(settings['vk_user_id'], settings['vk_token'])
    data = get_photo_data(settings['vk_user_id'], settings['vk_token'])
    count_photo = data['response']['count']
    print(f'Получено {count_photo} фотографий.\n')

    if count_photo == 0:
        print(f'Фотографии не обнаружены.\n')
        exit()

    bar = IncrementalBar('Обработка данных', max=count_photo)

    album = {}
    for photos in data["response"]["items"]:
        photo_name =  get_photo_name(f"{photos['likes']['count']}.jpg", photos['date'], album)
        photo = sorted(photos["sizes"],key=lambda x: x['type'])[-1]
        url = photo["url"]
        album[photo_name] = {'photo_name':photo_name, 'size':photo["type"], 'url':photo["url"]}
        bar.next()
        time.sleep(0.1)

    bar.finish()

    # pprint(album)
    print('\n',f'Данные обработаны. Загружаю на Yndex disk\n')

    # y_d = yadisk.YaDisk('','',settings['ya_token'])

    y_d = YandexDisk(settings['ya_token'])

    # print(settings['ya_token'])
    # print(y_d.check_token())

    path_to_file = input('Введите название каталога на диске (по умолчанию текущая дата): ')
    if path_to_file == "":
        path_to_file = str(datetime.now().date())

    if not y_d.exists(path_to_file):
        y_d.mkdir(path_to_file)

    count_photo_get = count_photo
    get_question = True
    while get_question:
        count_photo_get = input('Введите количество фотографий, которое хотите сохранить (0 - отмена): \n')
        if count_photo_get == '':
            print('Вы ввели пустое значение\n')
        elif count_photo_get == '0':
            get_question = False
            exit()
        else:
            get_question = False

    # bar = IncrementalBar('Загрузка фото на диск', max=int(count_photo_get))

    print('Загрузка фото на диск\n')

    list_json = []
    for filename, properties in sorted(album.items())[:int(count_photo_get)]:
        result = y_d.upload_url(properties["url"], f'{path_to_file}/{filename}')
        if result.status_code == 202:
            list_json.append({"file_name": filename, "size": properties["size"]})
            print(f'Добавлен файл {path_to_file}/{filename}.')
        else:
            print(f'Ошибка: ответ сервера - {result.status_code}.')

    path = os.path.join(os.getcwd(), 'result.json')
    with open(path, 'w', encoding='utf-8') as w_file:
        json.dump(list_json , w_file)