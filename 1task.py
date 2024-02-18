import requests
from bs4 import BeautifulSoup
from pathlib import Path
import datetime
import os, os.path


def has_1000_words(text):
    text = text.replace("\n", " ").replace("\r", "")
    return len(text.split()) >= 1000


def get_domain(ref):
    url_component = ref.split("/")
    return url_component[0] + "//" + url_component[2] + "/"


def get_inside_links(url):
    domain = get_domain(url)
    response = requests.get(url)
    soup = BeautifulSoup(response.text, features="html.parser")
    hrefs = []
    for a in soup.find_all("a"):
        try:
            if a.attrs:
                hrefs.append(a.attrs["href"])
        except Exception as e:
            print(e)
    # фильтрация внутренних ссылок
    links = list(
        filter(lambda ref: ref.startswith(domain) or ref.startswith("/"), hrefs)
    )
    # "/some_link" -> "http://domain.com/some_link"
    for i in range(0, len(links)):
        if links[i].startswith("/"):
            links[i] = domain + links[i][1:]
    return links


def get_content(url):
    response = requests.get(url)
    if "pdf" in response.headers["Content-Type"]:
        return ""
    html = response.text
    soup = BeautifulSoup(html, features="html.parser")
    return html


def is_100_pages(dir):
    return 100 < len(
        [name for name in os.listdir(dir) if os.path.isfile(os.path.join(dir, name))]
    )


def mkdir_for_pages():
    new_dir = "./%s" % datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    Path(new_dir).mkdir(parents=True, exist_ok=True)
    return new_dir


urls = [
    "https://www.business-gazeta.ru",
    "https://ru.wikipedia.org/",
    "https://mipt.ru/",
]

if __name__ == "__main__":
    new_dir = mkdir_for_pages()
    visited = []
    not_visited_urls = set([])
    idx = 0
    while True:
        if not not_visited_urls:
            not_visited_urls = set(urls) - set(visited)
        if is_100_pages(new_dir):
            break
        try:
            to_visit = not_visited_urls.pop()
        except Exception as e:
            print(e)
            break
        content = get_content(to_visit)
        visited.append(to_visit)
        urls += get_inside_links(to_visit)
        urls = list(set(urls))
        if not has_1000_words(content):
            # urls.remove(to_visit)
            continue
        # если нужно ограничить количество страниц, можно добавить проверку
        with open(f"./{new_dir}/{idx}.html", "a", encoding="utf-8") as f:
            f.write(content)
        with open(f"./{new_dir}/index.txt", "a", encoding="utf-8") as f:
            f.write(f"{to_visit}\n")
        idx += 1
