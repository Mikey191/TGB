import requests
from bs4 import BeautifulSoup
import json
from pars.config_pars import teams, getUrl, header
# import config
from datetime import datetime #для получения сегодняшней даты и времени

team = "челси"
current_datetime = datetime.now() #нужный формат "4 августа 2023", "11:42 МСК", а у нас 2023 08 04
url_champ = "https://www.championat.com/"
# url_connect = getUrl(team)

def format_date(data: datetime.date) -> str:
    """
    Функция для преобразования в нужный формат даты
    :param data: datetime.date
    :return: str
    """
    #['2023', '08', '04'] => ["4", "августа", "2023"] => "4 августа 2023"
    month = {
        "01": "января",
        "02": "февраля",
        "03": "марта",
        "04": "апреля",
        "05": "мая",
        "06": "июня",
        "07": "июля",
        "08": "августа",
        "09": "сентября",
        "10": "октября",
        "11": "ноября",
        "12": "декабря"
    }
    date = list(str(data).split("-"))
    new_date = []
    new_date.append(date[-1].replace("0", "") if date[-1].startswith("0") else date[-1])
    new_date.append(month[date[1]])
    new_date.append(date[0])

    return " ".join(new_date)

def format_time(data: datetime.time) -> str:
    # 14:59:59.197351 => 14:59 МСК
    """
    Функция для преобразования в нужный формат времени
    :param data: datetime.time
    :return: str
    """
    timezone = "МСК"
    return f"{str(data)[:5]} {timezone}"

def save_html_apl_table_page(team: str) -> None:
    """
    Cохраняет страницу в html файл для дальнейшей работы с ним.
    Функция предназначенна для тестов,
    что бы не обращаться по несколько раз во время теста к странице сайта
    :param team: str
    :return: None
    """
    req = requests.get(getUrl(team), headers=header)
    # req = requests.get(config.getUrl(team), headers=config.header)
    src = req.text
    with open("../data/index.html", "w", encoding="utf-8") as file:
        file.write(src)

def save_json_file(d: dict) -> None:
    with open("../data/team_news.json", "w", encoding="utf-8") as file:
        json.dump(d, file, indent=4, ensure_ascii=False)

def all_news_club_now_date() -> list:
    """
    Функция парсит последнии новости по клубу, переданому в аргумент
    :return: словарь новостей за сегоднящний день с сылками на каждую новость
    """
    #Читаем наш сохраненный файл и сохраняем в переменную src
    with open("../data/index.html", encoding="utf-8") as file:
        src = file.read()
    soup = BeautifulSoup(src, "lxml")
    # all_dates = soup.find_all(class_="news-items__head")
    all_news = soup.find_all(class_="news-item")
    all_news_href = []
    last_time = ""

    for item in all_news:
        item_date = format_date(current_datetime.date())
        item_time = item.find(class_="news-item__time").text
        item_text = item.find(class_="news-item__title").text
        item_href = item.find(class_="news-item__title").get("href")
        #проверка с костылями на новость. Она основанна на предположении, что у команды каждый день есть новости
        try:
            if int(item_time[:2]) > last_time:
                break
        except:
            pass
        all_news_href.append([item_date, item_time, item_text, url_champ+item_href])

        last_time = int(item_time[:2])

    return all_news_href

def pars_last_club_news(team: str) -> dict:
    print(f"Начинаем парсить с параметром '{team}'")
    """
    Функция парсит сайт с последней новостью о клубе
    :return: словарь типа {club: , news: , date: , time: , href: }
    """
    # Читаем наш сохраненный файл и сохраняем в переменную src
    # with open("../data/index.html", encoding="utf-8") as file:
    #     src = file.read()

    #или применяем коннект напрямую по ссылки
    req = requests.get(getUrl(team), headers=header)
    # req = requests.get(config.getUrl(team), headers=config.header)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    # all_dates = soup.find_all(class_="news-items__head")
    last_news = soup.find(class_="news-item")

    item_date = format_date(current_datetime.date())
    item_time = last_news.find(class_="news-item__time").text
    item_text = last_news.find(class_="news-item__title").text
    item_href = last_news.find(class_="news-item__title").get("href")

    return {
        "club": team,
        "news": item_text,
        "date": item_date,
        "time": item_time,
        "href": url_champ+item_href
    }


def pars_last_three_news(team: str) -> list | dict:
    """
    Функция парсит сайт и возвращает последнии три новости о клубе
    :param team:
    :return:
    """
    # Читаем наш сохраненный файл и сохраняем в переменную src
    # with open(r"C:\Users\whymk\Desktop\projects\project7\data\index.html", encoding="utf-8") as file:
    #     src = file.read()

    #или применяем коннект напрямую по ссылки
    req = requests.get(getUrl(team), headers=header)
    src = req.text
    soup = BeautifulSoup(src, "lxml")
    # all_dates = soup.find_all(class_="news-items__head")
    last_news = soup.find_all(class_="news-item")
    it = iter(last_news)
    lst_out = []
    for i in range(3):
        it_number = i+1
        it_club = team
        it_news = next(it).find(class_="news-item__title").text
        it_date = ""
        it_time = ""
        it_href = next(it).find(class_="news-item__title").get("href")
        lst_out.append({
            "number": it_number,
            "club": it_club,
            "news": it_news,
            "date": it_date,
            "time": it_time,
            "href": url_champ+it_href
        })

    return lst_out