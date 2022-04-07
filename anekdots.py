from bs4 import BeautifulSoup
import requests

url = 'https://www.anekdot.ru/random/anekdot/'


def anekdot_request():
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")
    anekdot = soup.find(class_='text')
    anekdot = str(anekdot)
    anekdot = anekdot.replace('<div class="text">', '')
    anekdot = anekdot.replace('<br/>', '\n')
    anekdot = anekdot.replace('</div>', '')
    return anekdot
