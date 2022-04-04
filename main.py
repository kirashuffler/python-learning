from http.client import HTTPSConnection
from html.parser import HTMLParser
from urllib.parse import urlparse


class HTMLParserWordCounter(HTMLParser):
    def __init__(self, word: str):
        self.word_count = 0
        self.search_word = word
        super().__init__()

    def handle_data(self, data: str) -> None:
        self.word_count += data.count(self.search_word)


def count_word_on_page(url: str, word: str) -> int:
    parsed_url = urlparse(url)
    connection = HTTPSConnection(parsed_url.hostname)
    connection.request("GET", parsed_url.path)
    connection_response = connection.getresponse()
    connection_data = connection_response.read()
    parser = HTMLParserWordCounter(word)
    parser.feed(connection_data.decode())
    return parser.word_count


optional_count = count_word_on_page('https://docs.python.org/3/library/urllib.parse.html',
                                    'optional')
print(optional_count)
