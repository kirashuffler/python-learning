import time
from http.client import HTTPSConnection
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.parse import urljoin


class CustomHTMLParser(HTMLParser):
    def __init__(self, word: str):
        self.links_set = set()
        self.word_count = 0
        self.search_word = word
        super().__init__()

    def handle_data(self, data: str) -> None:
        if '404' in data:
            return
        self.word_count += data.count(self.search_word)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == 'a' and 'href' == attrs[0][0] and '.html' in attrs[0][1]:
            self.links_set.add(attrs[0][1])


def generate_html_data(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.fragment != '':
        return 'none'
    connection = HTTPSConnection(parsed_url.hostname)
    connection.request("GET", parsed_url.path)
    connection_response = connection.getresponse()
    connection_data = connection_response.read()
    return connection_data.decode()


def count_word_on_page_and_subpages(url: str, word: str, visited_links=set()) -> int:
    count = 0
    html_data = generate_html_data(url)
    if html_data == 'none':
        return count
    parser = CustomHTMLParser(word)
    parser.feed(html_data)
    count += parser.word_count
    sublinks = set()
    for relative_link in parser.links_set:
        sublinks.add(urljoin(main_url, relative_link))
    visited_links.add(url)
    if len(sublinks) == 0:
        return count
    for link in sublinks:
        if link in visited_links:
            continue
        count += count_word_on_page_and_subpages(link, word, visited_links)
    return count


if __name__ == '__main__':
    main_url = 'https://docs.python.org/3/library/urllib.parse.html'
    start = time.time()
    n = count_word_on_page_and_subpages(main_url, 'optional')
    end = time.time()
    print("Elapsed time in seconds:", end - start)
    print(n)
