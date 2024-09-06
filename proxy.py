import requests
from bs4 import BeautifulSoup

response = requests.get('https://www.kino-teatr.ru/kino/movie/hollywood/21379/forum/').text
soup = BeautifulSoup(response, 'lxml')
string = soup.find('div', class_='comments_block comments_page').text
rows = string.split('\n')
print(rows)