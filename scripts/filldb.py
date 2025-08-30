import requests, random
from collections import namedtuple

API_URL = 'http://127.0.0.1:5000/api/v1/'
LOGIN_URL = API_URL + 'session/login/'
CATEGORIES_URL = API_URL + 'categories/' 
PRODUCTS_URL = API_URL + 'products/'
ADDRESSES_URL = API_URL + 'addresses/'
PRODUCT_COUNT = 20
ADDRESS_COUNT = 5

Category = namedtuple('Category' , 'name img')
CATEGORIES = [
    Category('Смартфоны', 'img/smartphones/1.png'),
    Category('Планшеты', 'img/tablets/1.png'),
    Category('Телефоны', 'img/phones/1.png')
]

auth = requests.post(LOGIN_URL, data={
    'login': 'admin',
    'password': 'a665a45920422f9d417e4867efdc4fb8a04a1f3fff1fa07e998e86f7f7a27ae3',    
})
for i, category in enumerate(CATEGORIES, start=1):
    data = { 'name': category.name}
    r = requests.post(CATEGORIES_URL, data=data, cookies=auth.cookies)
    print(f'{i}/{len(CATEGORIES)} {category.name} ({r.status_code})')
    if r.status_code != 201: exit()
    for j in range(1, PRODUCT_COUNT+1):
        data = {
            'name': f'{category.name[:-1]} #{j}',
            'cost': random.randint(10, 90) * 100,
            'img_path': category.img,
            'category_id': i,
            'count': random.randint(5, 50),
        }
        r = requests.post(PRODUCTS_URL, data=data, cookies=auth.cookies)
        print(f'Товар {j}/{PRODUCT_COUNT} ({r.status_code})')
for i in range(1, ADDRESS_COUNT+1):
    data = {
        'address': f'Тестовая ул. д.{i}',
        'city': 'Тестовый',
        'img_path': 'img/addresses/1.jpg'
    }
    r = requests.post(ADDRESSES_URL, data=data)
    print(f'Адрес {i}/{ADDRESS_COUNT} ({r.status_code})')
