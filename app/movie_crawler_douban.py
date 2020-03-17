from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options


import time


class DoubanMovieCrawler:
    def __init__(self):
        options = Options()
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--headless')
        self._driver = webdriver.Chrome(options=options, executable_path="/usr/bin/chromedriver")

        self._genres = ["剧情", "喜剧", "动作", "爱情", "科幻", "动画", "悬疑", "惊悚", "恐怖", "犯罪", "同性", "音乐", "歌舞", "传记", "历史", "战争",
                        "西部", "奇幻", "冒险", "灾难", "武侠", "情色"]
        self._regions = ["中国大陆", "美国", "中国香港", "中国台湾", "日本", "韩国", "英国", "法国", "德国", "意大利", "西班牙", "印度", "泰国", "俄罗斯",
                         "伊朗", "加拿大", "澳大利亚", "爱尔兰", "瑞典", "巴西", "丹麦"]
        self._max_actors = 5

    def open_page(self, url):
        self._driver.get(url)
        print(f"open movie page {url}")
        time.sleep(2)

    def close_page(self):
        print("close page")
        self._driver.quit()

    def find_elements_by(self, element, by, value):
        print(f"find {by} which value is '{value}'")
        if not element:
            return []
        try:
            return element.find_elements(by, value)
        except NoSuchElementException:
            print(f"not found {by} which value is '{value}'")
            return []

    def find_element_by(self, element, by, value):
        print(f"find {by} which value is '{value}'")
        if not element:
            return None
        try:
            return element.find_element(by, value)
        except NoSuchElementException:
            print(f"not found {by} which value is '{value}'")
            return None

    def extract_detail(self, movie):
        try:
            self.open_page(movie["douban_link"])
        except:
            return
        movie_detail_el = self.find_element_by(self._driver, By.ID, "info")

        movie_director_els = self.find_element_by(movie_detail_el, By.XPATH,
                                                  "//span[contains(text(), '导演')]//following-sibling::span")
        for movie_director_el in self.find_elements_by(movie_director_els, By.TAG_NAME, "a"):
            movie["director"].append(movie_director_el.text)

        movie_playwright_els = self.find_element_by(movie_detail_el, By.XPATH,
                                                    "//span[contains(text(), '编剧')]//following-sibling::span")
        for movie_playwright_el in self.find_elements_by(movie_playwright_els, By.TAG_NAME, "a"):
            movie["playwright"].append(movie_playwright_el.text)

        movie_actors_el = self.find_element_by(self.find_element_by(movie_detail_el, By.CLASS_NAME, "actor"),
                                               By.CLASS_NAME, "attrs")
        i = 0
        for movie_actor_el in self.find_elements_by(movie_actors_el, By.TAG_NAME, "a"):
            movie["cast"].append(movie_actor_el.text)
            i += 1
            if i >= self._max_actors:
                break
        self.close_page()
        return movie


    def extract_info(self, movie_page, min_score):
        self.open_page(movie_page)
        movies = []

        start = 0
        retry = 0

        current_score = 10
        movie_el_list = self.find_elements_by(self._driver, By.CLASS_NAME, "movie-content")
        while current_score >= min_score and start < len(movie_el_list):
            movie_el = movie_el_list[start]
            if not movie_el.text:
                if retry == 1:
                    break
                retry = 1
                self._driver.execute_script("return arguments[0].scrollIntoView()", movie_el_list[start-1])
                time.sleep(5)
                movie_el_list = self.find_elements_by(self._driver, By.CLASS_NAME, "movie-content")
                continue
            retry = 0
            start += 1
            movie = {}
            movie["genres"] = []
            movie["regions"] = []
            movie["director"] = []
            movie["playwright"] = []
            movie["cast"] = []
            current_score = float(self.find_element_by(movie_el, By.CLASS_NAME, "rating_num").text)
            movie["rating"] = current_score
            img_el = self.find_element_by(movie_el, By.CLASS_NAME, "movie-img")
            if img_el:
                movie["post"] = img_el.get_attribute("data-original")
            else:
                print("Not found img")


            movie_link_el = self.find_element_by(self.find_element_by(movie_el, By.CLASS_NAME, "movie-name"),
                                                 By.TAG_NAME, "a")
            if movie_link_el:
                movie["douban_link"] = movie_link_el.get_attribute("href")
                movie["name"] = movie_link_el.text
            else:
                continue
            movie_misc_el = self.find_element_by(movie_el, By.CLASS_NAME, "movie-misc")
            if movie_misc_el:
                movie_misc = movie_misc_el.text
                for word in movie_misc.split("/"):
                    word = word.strip()
                    if DoubanMovieCrawler._to_int(word):
                        movie["year"] = int(word)
                    else:
                        if word in self._genres:
                            movie["genres"].append(word)
                        elif word in self._regions:
                            movie["regions"].append(word)

            movies.append(movie)
            movie_el_list = self.find_elements_by(self._driver, By.CLASS_NAME, "movie-content")
        self.close_page()
        return movies

    @staticmethod
    def _to_int(word):
        try:
            int(word)
            return True
        except ValueError:
            return False


if __name__ == "__main__":
    test = DoubanMovieCrawler()

    movies = test.extract_info()
    for movie in movies:
        test.extract_detail(movie)
    print(movies)
