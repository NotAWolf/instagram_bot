from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
import time
import random
import requests
import os
import json
import eel


class InstagramBot():

    # обращаемся к драйверу
    def __init__(self):
        self.browser = webdriver.Chrome('./driver/chromedriver')

    # метод для закрытия вкладки и браузера
    def close_browser(self):
        self.browser.close()
        self.browser.quit()

    # метод для авторизации
    def login(self, username, password):
        browser = self.browser

        browser.get('https://www.instagram.com')
        time.sleep(random.randrange(3, 5))

        username_input = browser.find_element_by_name('username')
        username_input.clear()
        username_input.send_keys(username)

        time.sleep(2)

        password_input = browser.find_element_by_name('password')
        password_input.clear()
        password_input.send_keys(password)

        password_input.send_keys(Keys.ENTER)
        time.sleep(5)

        # закрываем всплывающие окна
        browser.find_element_by_xpath('/html/body/div[1]/section/main/div/div/div/div/button').click()
        browser.find_element_by_xpath('/html/body/div[5]/div/div/div/div[3]/button[2]').click()

    # метод для простановки лайков по #
    def like_photo_by_hashtag(self, hashtag):
        browser = self.browser
        browser.get(f'https://www.instagram.com/explore/tags/{hashtag}/')
        time.sleep(3)

        for i in range(1, 30):
            browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(random.randrange(3, 5))

        hrefs = browser.find_elements_by_tag_name('a')

        # забираем все ссылки и сохраняем их в списоке, если в них содержится строка /p/
        posts = [item.get_attribute('href') for item in hrefs if '/p/' in item.get_attribute('href')]

        for url in posts:
            try:
                browser.get(url)
                time.sleep(3)
                browser.find_element_by_xpath(
                    '/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button').click()
                time.sleep(random.randrange(120, 200))
            except Exception as ex:
                print(ex)
                self.close_browser()

    # метод для для проверки xpath
    def xpath_exists(self, url):
        browser = self.browser
        try:
            browser.find_element_by_xpath(url)
            exist = True
        except NoSuchElementException:
            exist = False
        return exist

    # метод для получения ссылок постов со страницы пользователя
    def get_all_posts_urls(self, userpage):
        browser = self.browser
        browser.get(userpage)
        time.sleep(5)

        wrong_userpage = '/html/body/div[1]/section/main/div/div/h2'
        if self.xpath_exists(wrong_userpage):
            print('Такого пользователя не существует, проверьте URL')
            self.close_browser()
        else:
            print('Пользователь успешно найден.')
            time.sleep(2)

            # считываем кол-во постов, сохраняем их в список и прогружаем страницу соответственно
            posts_count = int(browser.find_element_by_xpath(
                '/html/body/div[1]/section/main/div/header/section/ul/li[1]/span/span').text)
            loops_count = int(posts_count / 12)
            print(loops_count)

            posts_urls = []
            for i in range(0, loops_count):
                hrefs = browser.find_elements_by_tag_name('a')
                hrefs = [item.get_attribute('href') for item in hrefs if '/p/' in item.get_attribute('href')]

                for href in hrefs:
                    posts_urls.append(href)

                browser.execute_script('window.scrollTo(0, document.body.scrollHeight);')
                time.sleep(random.randrange(2, 4))
                print(f'Итерация №{i}')

            file_name = userpage.split('/')[-2]

            # преобразем список в множество, чтобы избавиться от дублирования
            set_posts_urls = set(posts_urls)
            set_posts_urls = list(set_posts_urls)

            with open(f'{file_name}_set.txt', 'a') as file:
                for post_url in set_posts_urls:
                    file.write(post_url + '\n')

    # метод для простоновки лайков пользователю
    def put_many_likes(self, userpage):
        browser = self.browser
        self.get_all_posts_urls(userpage)
        file_name = userpage.split('/')[-2]
        time.sleep(4)
        browser.get(userpage)
        time.sleep(4)

        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            for post_url in urls_list:
                try:
                    browser.get(post_url)
                    time.sleep(3)

                    like_button = '/html/body/div[1]/section/main/div/div[1]/article/div[3]/section[1]/span[1]/button'
                    browser.find_element_by_xpath(like_button).click()
                    time.sleep(random.randrange(130, 200))
                    print(f'Лайк на пост: {post_url} поставлен.')
                except Exception as ex:
                    print(ex)
                    self.close_browser()

            self.close_browser()

    # метод для скачивания фото пользователя
    def download_userpage_content(self, userpage):
        browser = self.browser
        self.get_all_posts_urls(userpage)
        file_name = userpage.split('/')[-2]
        time.sleep(4)
        browser.get(userpage)
        time.sleep(4)

        if os.path.exists(f'{file_name}'):
            print('Папак уже существует')
        else:
            os.mkdir(file_name)

        img_src_urls = []
        with open(f'{file_name}_set.txt') as file:
            urls_list = file.readlines()

            for post_url in urls_list:
                try:
                    browser.get(post_url)
                    time.sleep(5)

                    img_src = '/html/body/div[1]/section/main/div/div[1]/article/div[2]/div/div/div[1]/img'
                    post_id = post_url.split('/')[-2]

                    if self.xpath_exists(img_src):
                        img_src_url = browser.find_element_by_xpath(img_src).get_attribute('src')
                        img_src_urls.append(img_src_url)

                        # сохраняем изображение
                        get_img = requests.get(img_src_url)
                        with open (f'{file_name}/{file_name}_{post_id}_img.jpg', 'wb') as img_file:
                            img_file.write(get_img.content)

                    else:
                        print('Что-то пошло нетак.')
                        img_src_urls.append(f'{post_url}, нет ссылки')

                    print(f'Контент из поста {post_url} скачен')

                except Exception as ex:
                    print(ex)
                    self.close_browser()

            self.close_browser()

        with open (f'{file_name}/{file_name}_img_src_urls.txt', 'a') as file:
            for i in img_src_urls:
                file.write(i + '\n')

    # метод для подписки
    def get_all_followers(self, userpage):
        browser = self.browser
        browser.get(userpage)
        time.sleep(5)
        file_name = userpage.split('/')[-2]

        if os.path.exists(f'{file_name}'):
            print(f'Папка {file_name} уже существует')
        else:
            os.mkdir(file_name)

        wrong_userpage = '/html/body/div[1]/section/main/div/div/h2'
        if self.xpath_exists(wrong_userpage):
            print(f'Пользователя {file_name} не существует, проверьте URL')
            self.close_browser()
        else:
            print(f'Пользователь {file_name} успешно найден.')
            time.sleep(2)

            followers_button = browser.find_element_by_xpath('/html/body/div[1]/section/main/div/header/section/ul/li[2]/a/span')
            followers_count = followers_button.get_attribute('title')

            # если число > 1000
            if ' ' in followers_count:
                followers_count = int(''.join(followers_count.split(' ')))
            else:
                followers_count = int(followers_count)
            print(f'Колличество подписчиков {followers_count}')
            time.sleep(2)
            loops_count = int(followers_count / 12)
            print(f'Число итераций:{loops_count}')
            time.sleep(2)
            followers_button.click()
            followers_ul = browser.find_element_by_xpath('/html/body/div[6]/div/div/div[2]')
            try:
                followers_urls = []
                # скролим окно
                for i in range(1, loops_count + 1):
                    browser.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", followers_ul)
                    time.sleep(random.randrange(2, 4))
                    print(f'Итерация №{i}')

                # сохраняем url-адреса пользователей
                all_urls_div = followers_ul.find_elements_by_tag_name('li')
                for url in all_urls_div:
                    url = url.find_element_by_tag_name("a").get_attribute("href")
                    followers_urls.append(url)

                with open(f'{file_name}/{file_name}.txt', 'a') as text_file:
                    for link in followers_urls:
                        text_file.write(link + '\n')

                with open(f"{file_name}/{file_name}.txt") as text_file:
                    users_urls = text_file.readlines()

                    for user in users_urls:
                        try:
                            try:
                                with open(f'{file_name}/{file_name}_subscribe_list.txt',
                                          'r') as subscribe_list_file:
                                    lines = subscribe_list_file.readlines()

                                    # проверяем, подписаны ли уже на пользователя
                                    if user in lines:
                                        print(f'Мы уже подписаны на {user}, переходим к следующему пользователю!')
                                        continue

                            except Exception as ex:
                                print('Файл со ссылками ещё не создан!')
                                print(ex)

                            browser = self.browser
                            browser.get(user)
                            page_owner = user.split("/")[-2]

                            if self.xpath_exists("/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/a"):

                                print("Это наш профиль, уже подписан, пропускаем итерацию!")
                            elif self.xpath_exists(
                                    "/html/body/div[1]/section/main/div/header/section/div[1]/div[2]/div/div[2]/div/span/span[1]/button/div/span"):
                                print(f"Уже подписаны, на {page_owner} пропускаем итерацию!")
                            else:
                                time.sleep(random.randrange(4, 8))

                                # если аккаунт закрытый
                                if self.xpath_exists(
                                        "/html/body/div[1]/section/main/div/div/article/div[1]/div/h2"):
                                    try:
                                        if self.xpath_exists(
                                                "/html/body/div[1]/section/main/div/header/section/div[2]/div/div/button"):
                                            follow_button = browser.find_element_by_xpath(
                                                "/html/body/div[1]/section/main/div/header/section/div[2]/div/div/button").click()
                                            print(f'Запросили подписку на пользователя {page_owner}. Закрытый аккаунт!')
                                        else:
                                            follow_button = browser.find_element_by_xpath(
                                                "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/button").click()
                                            print(f'Запросили подписку на пользователя {page_owner}. Закрытый аккаунт!')

                                    except Exception as ex:
                                        print(ex)
                                else:
                                    try:
                                        if self.xpath_exists(
                                                "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/button"):
                                            follow_button = browser.find_element_by_xpath(
                                                "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/button").click()
                                            print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')

                                        else:
                                            follow_button = browser.find_element_by_xpath(
                                                "/html/body/div[1]/section/main/div/header/section/div[1]/div[1]/div/div/div/span/span[1]/button").click()
                                            print(f'Подписались на пользователя {page_owner}. Открытый аккаунт!')

                                    except Exception as ex:
                                        print(ex)

                                with open(f'{file_name}/{file_name}_subscribe_list.txt',
                                          'a') as subscribe_list_file:
                                    subscribe_list_file.write(user)

                                time.sleep(random.randrange(120, 280))

                        except Exception as ex:
                            print(ex)
                            self.close_browser()

            except Exception as ex:
                print(ex)
                self.close_browser()

        self.close_browser()

    # методо по отписке
    def unsubscribe_for_all_users(self, userpage):

        browser = self.browser
        browser.get(userpage)
        time.sleep(random.randrange(3, 6))

        following_button = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[3]/a")
        following_count = following_button.find_element_by_tag_name("span").text

        if ' ' in following_count:
            following_count = int(''.join(following_count.split(' ')))
        else:
            following_count = int(following_count)

        print(f"Количество подписок: {following_count}")

        time.sleep(random.randrange(2, 4))

        loops_count = int(following_count / 10) + 1
        print(f"Количество перезагрузок страницы: {loops_count}")

        following_users_dict = {}

        for loop in range(1, loops_count + 1):

            count = 10
            browser.get(userpage)
            time.sleep(random.randrange(3, 6))

            following_button = browser.find_element_by_xpath("/html/body/div[1]/section/main/div/header/section/ul/li[3]/a")

            following_button.click()
            time.sleep(random.randrange(3, 6))

            following_div_block = browser.find_element_by_xpath("/html/body/div[6]/div/div/div[3]/ul/div")
            following_users = following_div_block.find_elements_by_tag_name("li")
            time.sleep(random.randrange(3, 6))

            for user in following_users:

                # после 10 отписок обновляем страницу и начинаем заново
                if not count:
                    break

                user_url = user.find_element_by_tag_name("a").get_attribute("href")
                user_name = user_url.split("/")[-2]

                following_users_dict[user_name] = user_url

                following_button = user.find_element_by_tag_name("button").click()
                time.sleep(random.randrange(3, 6))
                unfollow_button = browser.find_element_by_xpath("/html/body/div[7]/div/div/div/div[3]/button[1]").click()

                print(f"Итерация #{count} >>> Отписался от пользователя {user_name}")
                count -= 1

                time.sleep(random.randrange(120, 130))

        with open("following_users_dict.txt", "w", encoding="utf-8") as file:
            json.dump(following_users_dict, file)

        self.close_browser()

# функции для eel, так как библиотека не поддерживает вызов методов через экземпляр класса
@eel.expose
def put_like(username, password, userpage):
    my_bot = InstagramBot()
    my_bot.login(username, password)
    my_bot.put_many_likes(userpage)

@eel.expose
def get_followers(username, password, userpage):
    my_bot = InstagramBot()
    my_bot.login(username, password)
    my_bot.get_all_followers(userpage)

@eel.expose
def download_content(username, password, userpage):
    my_bot = InstagramBot()
    my_bot.login(username, password)
    my_bot.download_userpage_content(userpage)

@eel.expose
def unfollow_users(username, password, userpage):
    my_bot = InstagramBot()
    my_bot.login(username, password)
    my_bot.unsubscribe_for_all_users(userpage)

@eel.expose
def like_by_hashtag(username, password, hashtag):
    my_bot = InstagramBot()
    my_bot.login(username, password)
    my_bot.like_photo_by_hashtag(hashtag)


eel.init('./web/')
eel.start('mane.html', size=(700, 700))

