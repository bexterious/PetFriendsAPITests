from api import PetFriends  #api.py
from settings import valid_email, valid_password, invalid_email, invalid_password    #settings.py
import os

pf = PetFriends() #просто переименовываем

"""ниже блок с простеньким тестом для валидного юзера
получил ли он ответ с кодом 200 и есть ли в результате ключ"""
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)    #гет в файле api
    assert status == 200
    assert 'key' in result

"""ниже такой же тест, но для невалидного юзера
меняем название, вводим верное мыло и невалидный пароль"""
def test_get_api_key_for_invalid_pass(email=valid_email, password=invalid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert result == 403

"""верный пароль, но невалидное мыло, чтобы наверняка убедиться, что пропускаются только верные комбинации
как и выше, проверяем, что юзер получит код из документации"""
def test_get_api_key_for_invalid_email(email=invalid_email, password=valid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert result == 403

#ниже этот гет, но для невалидной пары
def test_get_api_key_for_invalid_user(email=invalid_email, password=invalid_password):
    status, result = pf.get_api_key(email, password)
    assert status == 403
    assert result == 403



"""ниже функция для списка питомцев
получаем ключ, запрашиваем список и проверяем, что ответ 200 и список не пустой"""
def test_get_all_pets_with_valid_key(filter=''):    #сейчас там доступен только 1 фильтр
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.get_list_of_pets(auth_key, filter)
    assert status == 200
    assert len(result['pets']) > 0

"""и ее функция с невалидными данными
мы не получим статус, потому что мы не получим ключ, чтобы подставить его в get_list"""
def test_get_all_pets_with_invalid_key(filter=''):
    _, auth_key = pf.get_api_key(invalid_email, invalid_password)
    if auth_key is not str:
        raise Exception("no")
    else:
        status, result = pf.get_list_of_pets(auth_key, filter)
        assert status == 403
        assert len(result['pets']) == 0



#добавление нового питомца

def test_add_new_pet_with_valid_data(name='Джоуль', animal_type='шотландец', age='4', pet_photo='images/cat1.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)   #получаем и обзываем ключ
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)    #добавляем всю инфу
    assert status == 200    #проверяем ответ от сервера, что все ок
    assert result['name'] == name   #и что хотя бы имя у нового питомца Джоуль

#тоже добавление, но с некорректными данными

def test_add_new_pet_with_invalid_data(name='Джоуль', animal_type='шотландец', age='20', pet_photo='images/cat1.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)
    assert status == 400
    assert result['name'] != name   #проверяем откат



#тестируем удаление
def test_successful_delete_self_pet():
    _, auth_key = pf.get_api_key(valid_email, valid_password)   #гетим ключ
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")   #гетим список питомцев
    if len(my_pets['pets']) == 0:   #если длина json соответствует 0
        pf.add_new_pet(auth_key, "Лейбниц", "кот", '3', "images/cat2.jpg") #то добавляем инфу о новом питомце
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")   #просим список питомцев
    pet_id = my_pets['pets'][0]['id']   #обзываем айди, идем к json, берем первыЙ (0й) айди из списка
    status, _ = pf.delete_pet(auth_key, pet_id) #запрашиваем удаление
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")   #запрашиваем список питомцев
    assert status == 200
    assert pet_id not in my_pets.values()   #теперь удаленного айди не должно быть в списке

#тоже удаление, но несуществующего питомца, чтобы доказать или опровергнуть существование призраков
def test_unsuccessful_delete_self_pet():
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    pet_id = 'ghost'
    status, _ = pf.delete_pet(auth_key, pet_id)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    assert status == 403


"""обновление информации о питомце
работает, если список не пуст, меняет первого зверя в списке
иначе ругает"""
def test_successful_update_self_pet_info(name='Фейнман', animal_type='кот', age='3'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['name'] == name
    else:
        raise Exception("There is no my pets")

#и негативное обновление
def test_unsuccessful_update_self_pet_info(name='Генри', animal_type='фрфыр', age='-3'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 400
        assert result['name'] != name
    else:
        raise Exception("There is no my pets")
#тест провалится и инфа обновится, хотя так быть не должно



def test_simple_add_new_pet_with_valid_data(name='Джоуль', animal_type='шотландец', age='4'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 200
    assert result['name'] == name

def test_simple_add_new_pet_with_unvalid_data(name='Фарадей', animal_type='0', age='4'):
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    status, result = pf.add_new_pet_without_photo(auth_key, name, animal_type, age)
    assert status == 400
    assert result['name'] != name



def test_add_photo_with_valid_data(pet_photo='images/cat2.jpg'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)  #определяем фото
    _, auth_key = pf.get_api_key(valid_email, valid_password)   #получаем ключ
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")   #получаем список зверей
    if len(my_pets['pets']) > 0:    #если больше нуля
        pet_id = my_pets['pets'][0]['id']   #то берем айди первого
        status, result = pf.add_new_photo(auth_key, pet_id, pet_photo)   #добавляем фото
        assert status == 200
        assert result['pet_photo'] == pet_photo
    else:
        raise Exception("There is no my pets")  #иначе ругаемся


def test_add_photo_with_valid_data(pet_photo='indigo.gif'):
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    _, auth_key = pf.get_api_key(valid_email, valid_password)
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
    if len(my_pets['pets']) > 0:
        pet_id = my_pets['pets'][0]['id']
        status, result = pf.add_new_photo(auth_key, pet_id, pet_photo)
        assert status == 400    #или 403
        assert result['pet_photo'] != pet_photo
    else:
        raise Exception("There is no my pets")