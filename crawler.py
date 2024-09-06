# У парсера есть огромная проблема - успешно он парсит только первую страницу, а дальше сайт запрашивает капчу
# Для решения проблемы я пробовал следующее
# Выставлял различное время для sleep на разных участках программы
# Менял куки из набора моих, пробовал генерировать случайные
# Использовал selenium, но он так же запрашивал капчу, и каждый раз проходить ее - ад
# Брал бесплатные прокси сервера для смены ip запроса. Может быть это бы и сработало, но я попробовал три сервиса
# Ни один ни дал хороших рабочих ip (я на 95 процентов уверен, что делал все правильно)
# Если не учитывать эту проблему, то парсер заполняет базу данных, логин и пароль установите в config.py
# Простите за мусор в коде, но так хотя бы видно, что я старался :(


import requests
from bs4 import BeautifulSoup
import psycopg2
import time
import math
import random
import re
from config import host, user_name, password

my_proxies = []
proxy_index = 0
max_proxy_index = 0

def get_proxy():
    global my_proxies
    global proxy_index
    global max_proxy_index
    if my_proxies == []:
        response = requests.get('https://free-proxy-list.net/').text
        soup = BeautifulSoup(response, 'lxml')
        ips_info = soup.find_all('table', class_='table table-striped table-bordered')
        for item in ips_info:
            ips = item.find('tbody').find_all('tr')
            for elem in ips:
                ip = elem.find_all('td')[0]
                port = elem.find_all('td')[1]
                proxy = ip.text + ':' + port.text
                my_proxies.append(proxy)
        max_proxy_index = len(my_proxies)
    if (proxy_index == max_proxy_index):
        proxy_index = 0
    proxies = {
        'https': str('http://' + my_proxies[proxy_index])
    }
    proxy_index += 1
    return proxies


def correct_name(name, review_count):
    name = re.sub("\(.*?\)","", name)
    name_copy = name.replace('№ ' + str(review_count),'')
    if name_copy != name:
        return name_copy
    name = name.replace('№ ', '')
    name_copy = name
    for ch in name:
        if not ch.isdigit():
            break
        else:
            name_copy[1:]
    return name_copy


def getReviews(string):
    rows = string.split('\n')
    review_count = 0
    reviews, names, dates = [], [], []
    for i in rows:
        if not i.find('сообщить модератору'):
            review_count += 1
    if review_count == 0:
        return 0, [], [], []
    count = review_count
    text = ''
    parce_need = False
    for row in rows:
        if not row.find('№'):
            if row.find('\xa0') < 0:
                continue
            row = correct_name(row, review_count)
            if row.find(')') != -1:
                name = row.split(' (')[0]
                date = row.split(')')[1].replace('\xa0 \xa0 ', '')
            else:
                parts = row.split('\xa0')
                name = parts[0].rstrip()
                for i in range(1, len(parts)):
                    if parts[i].find('.') > 0:
                        date = parts[i].lstrip().rstrip()
                        break
            parce_need = True
            continue
        if not row.find('сообщить модератору'):
            reviews.append(text)
            names.append(name)
            dates.append(date)
            text = ''
            review_count-=1
            parce_need = False
            continue
        if parce_need:
            text += row

    return count, names, dates, reviews

def get_random_cookie():
    digits = [i for i in range(0, 10)]

    random_str = ""

    for i in range(6):
        index = math.floor(random.random() * 10)
        random_str += str(digits[index])

    cookies = { 'kt_init': 'aHR0cHM6Ly95YW5kZXgucnUv',
    'tmr_lvid': '03267e05bdecab750f41d66968b1eb9e',
    'tmr_lvidTS': '1714814529807',
    '_ym_uid': '171481453069817471',
    '_ym_d': '1714814530',
    '_ga': 'GA1.1.158650497.1714814530',
    'domain_sid': 'V1wV3C9wuUcW1mzMxNMsl%3A1715873383541',
    'kt_forum_sort': 'desc',
    '_ym_isad': '1',
    '_ym_visorc': 'b',
    'PHPSESSID': '2j98nqm8i769ahc4a5dkb15001',
    '_ga_WQDK6H6G9C': 'GS1.1.1716039647.19.1.1716040468.0.0.0',
    'kt_forum_sort': 'desc',
    'tmr_detect': '1%7C1716040' + random_str,
    '_ga_WQDK6H6G9C': 'GS1.1.1715967219.16.1.1715968612.0.0.0',
    }
    return cookies

def get_random_sleep_time():
    return random.randint(1, 5)
    

def parceData():
    url = 'https://www.kino-teatr.ru/kino/movie/latin/'
    website = 'https://www.kino-teatr.ru'

    cookies = { 
    'kt_init': 'aHR0cHM6Ly95YW5kZXgucnUv',
    'tmr_lvid': '03267e05bdecab750f41d66968b1eb9e',
    'tmr_lvidTS': '1714814529807',
    '_ym_uid': '171481453069817471',
    '_ym_d': '1714814530',
    '_ga': 'GA1.1.158650497.1714814530',
    'kt_forum_sort': 'desc',
    '_ym_isad': '1',
    '_ym_visorc': 'b',
    'domain_sid': 'V1wV3C9wuUcW1mzMxNMsl%3A1716047417703',
    'PHPSESSID': '76fo3rh85urr4hm9sev2k55e60',
    '_ga_WQDK6H6G9C': 'GS1.1.1716047416.20.1.1716048011.0.0.0',
    'tmr_detect': '1%7C1716048011720',
    'kt_forum_sort': 'desc'
    }


    headers = {
        'authority': 'www.kino-teatr.ru',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'accept-language': 'ru,en;q=0.9',
        'cache-control': 'max-age=0',
        'referer': 'https://www.kino-teatr.ru/',
        'sec-ch-ua': '"Chromium";v="122", "Not(A:Brand";v="24", "YaBrowser";v="24.4", "Yowser";v="2.5"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/24.4.0.0 Safari/537.36',
    }
    # service = webdriver.FirefoxService(executable_path="C:\Proga\geckodriver.exe")
    # options = webdriver.FirefoxOptions()
    # options.binary_location = r"C:\Program Files\Mozilla Firefox\firefox.exe"
    # options.set_preference("general.useragent.override", "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.90 Safari/537.36")

    letters = [ 'a','b', 'v', 'g', 'd', 'e', 'j', 'z', 'i', 'k', 'l', 'm', 'n', 'o', 'p',
                'r', 's', 't', 'u', 'f', 'x', 'c', 'cz', 'sh', 'sch', 'ye', 'yu', 'ya', 'ENG', '0~9']

    id = 0
    names, years, countries, scores, reviews_counts, all_reviews = [],[],[],[], [], []
    resp = requests.Session()

    for l in letters:
        max_page = 1
        url_letter = url + l + '/'
        
        # driver = webdriver.Firefox(
        #     options=options,
        #     service=service
        # )
        #response = driver.get(url_letter)
        response = resp.get(url_letter, headers=headers, cookies=cookies).text
        soup = BeautifulSoup(response, 'lxml')
        hash_films = dict()
        print('Now parcing letter', l)
        r = soup.find('div', class_='page_numbers')
        if r != None:
            max_page = int(r.text.split()[-2])
        for page in range(1, max_page + 1):
            print('Now parcing page', page)
            final_url = url_letter + 'm' + str(page)
            final_response = resp.get(final_url, headers=headers, cookies=cookies).text
            final_soup = BeautifulSoup(final_response, 'lxml')
            films = final_soup.find_all('div', class_='list_item_details')
            for item in films:
                details = item.text
                rows = details.split('\n')[1:]
                name = rows[0].split(' |')[0]
                year, country = '', ''
                for i in rows:
                    if not i.find('Год'):
                        year = i.split(': ')[1].split(',')[0]
                        continue
                    if not i.find('Страна'):
                        country = i.split(': ')[1].split(',')[0] # Будем брать первую страну из списка
                        break
                href = item.find('a', href=True)['href']
                film_response = resp.get(website + href, headers=headers, cookies=cookies).text
                print('Parsing', name)
                film_soup = BeautifulSoup(film_response, 'lxml') 
                info = film_soup.find('span', class_='nowrap rating_digits')
                score = -1 if info is None else float(info.text.split(' /')[0])
                string = name + year + country + str(score)
                if (hash(string) not in hash_films):
                    hash_films[hash(string)] = id
                else:
                    continue
                names.append(name)
                years.append(year)
                countries.append(country)
                scores.append(score)
                #print(name)
                id+=1
                href = href.replace('annot/', '')
                review_response = resp.get(website + href + 'forum', headers=headers, cookies=cookies).text
                review_soup = BeautifulSoup(review_response, 'lxml')
                reviews = review_soup.find('div', class_='comments_block comments_page')
                if reviews != None:
                    count, review_names, review_dates, reviews_text = getReviews(reviews.text)
                    all_reviews.append([id, review_names, review_dates, reviews_text])
                    reviews_counts.append(count)
                else:
                    reviews_counts.append(0)
                    all_reviews.append([-1, [], [], []])
        hash_films.clear()
    return names, years, countries, scores, reviews_counts, all_reviews
            
def create_connection(db = ''):
    if db == '':
        with psycopg2.connect(
            host=host,
            user=user_name,
            password=password
        ) as conn:
            conn.autocommit = True
            print('Connection successful')
            with conn.cursor() as cursor:
                return conn, cursor
    else:
        with psycopg2.connect(
            host=host,
            user=user_name,
            password=password
        ) as conn:
            conn.autocommit = True
            print('Connection successful')
            with conn.cursor() as cursor:
                return conn, cursor

                
def create_user(cursor):
    cursor.execute('''CREATE ROLE film_user WITH LOGIN CREATEDB PASSWORD '1234' ''')

def delete_user(cursor):
    cursor.execute('''DROP USER IF EXISTS film_user''')

def create_tables(cursor):
    cursor.execute('''CREATE TABLE films(id serial, name text, score float, year int, country text, review_count int);
                      CREATE TABLE reviews(id serial, author text, data date, review_text text);
                      CREATE TABLE correspondence(film_id int, review_id int);''')
def delete_tables(cursor):
    cursor.execute('''DROP TABLE IF EXISTS films;
                      DROP TABLE IF EXISTS reviews;
                      DROP TABLE IF EXISTS correspondence;''')
    
def get_sql_insert_command_to_films(names, years, countries, scores, reviews_counts):
    res = ''
    for i in range(len(names)):
        if i != 0:
            res += ',\n'
        score = str(scores[i]) if scores[i] >= 0 else 'NULL'
        res += '(' + str(i + 1) + ',' + "'"  + str(names[i]) + "'" + ',' + score + ',' + str(years[i]) + ',' \
        + "'" + str(countries[i]) + "'" + ',' + str(reviews_counts[i]) + ')'
    return res

def get_sql_insert_command_to_reviews(all_reviews):
    res_reviews = ''
    res_correspondence = ''
    rev_id = 1
    for i in range(len(all_reviews)):
        if len(all_reviews[i][1]) == 0:
            continue
        if i != 0 and res_reviews != '':
            res_reviews += ',\n'
            res_correspondence += ',\n'
        for j in range(len(all_reviews[i][1])):
            if j != 0:
                res_reviews += ',\n'
                res_correspondence += ',\n'
            res_reviews += '(' + str(rev_id) + ',' + "'" + all_reviews[i][1][j] + "'" + ',' + "'" + str(all_reviews[i][2][j]) + "'" + ',' \
            + "'" + all_reviews[i][3][j].replace("'", '"') + "'" + ')'
            res_correspondence += '(' + str(all_reviews[i][0]) + ',' + str(rev_id) + ')'
            rev_id+=1
    return res_reviews, res_correspondence

def get_sql_insert_command_to_correspondence(all_reviews):
    res = ''

def insert_data(cursor, names, years, countries, scores, reviews_counts,  all_reviews):
    command_films = get_sql_insert_command_to_films(names, years, countries, scores, reviews_counts)
    if command_films == '':
        raise('No data to add')
    command_reviews, command_correspondence = get_sql_insert_command_to_reviews(all_reviews)
    cursor.execute('INSERT INTO films VALUES\n' + command_films)
    print('Inserting into films succesful')
    cursor.execute('INSERT INTO reviews VALUES\n' + command_reviews)
    print('Inserting into reviews succesful')
    cursor.execute('INSERT INTO correspondence VALUES\n' + command_correspondence)
    print('Inserting into correspondence succesful')



def crawl():
    try:
        connection = psycopg2.connect(
                    host=host,
                    user=user_name,
                    password=password
                )
        connection.autocommit = True
        print('Connection to postgre successful')
        cursor = connection.cursor()
        delete_user(cursor)
        create_user(cursor)    
        cursor.execute('''drop database if exists films_info_and_reviews;''')
        cursor.execute('''create database films_info_and_reviews;''')
        print('Recreating database successful')
    except psycopg2.Error as e:
        print(e)     
        connection.close()
        quit()
    finally:
        connection.close()

    try:
        connection = psycopg2.connect(
                    host=host,
                    user=user_name,
                    password=password,
                    database = 'films_info_and_reviews'
                )
        connection.autocommit = True
        print('Connection to postgre and database successful')
        cursor = connection.cursor()
        create_tables(cursor) 
        print('Creating tables successful')
        names, years, countries, scores, reviews_counts, all_reviews = parceData()
        insert_data(cursor, names, years, countries, scores, reviews_counts, all_reviews)
    except psycopg2.Error as e:
        print(e)     
        connection.close()
        quit()
    finally:
        print('Crawler algorithm done')
        connection.close()

# from sqlalchemy import create_engine

# host = 'localhost'
# user_name = 'postgres'
# password = 'admin'
# db_name = 'films_info_and_reviews'

# try:
#     with psycopg2.connect(
#         host=host,
#         user=user_name,
#         password=password,
#         database=db_name
#     ) as conn:
#         conn.autocommit = True
#         with conn.cursor() as cursor:
#             cursor.execute('SELECT * FROM films')
#             print('Connection successful')
#             print(cursor.fetchone())
# except psycopg2.Error as e:
#     print(e)
            
        