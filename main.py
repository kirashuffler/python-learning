import yappi
from http.client import HTTPSConnection
from html.parser import HTMLParser
from urllib.parse import urlparse
from urllib.parse import urljoin

number_of_requests = 0


class CustomHTMLParser(HTMLParser):
    def __init__(self, word: str):
        self.links_set = set()
        self.word_count = 0
        self.search_word = word
        super().__init__()

    def handle_data(self, data: str) -> None:
        self.word_count += data.count(self.search_word)

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if len(attrs) > 0 and 'href' == attrs[0][0] and '.html' in attrs[0][1]:
            self.links_set.add(attrs[0][1])


def fetch_html_data(url: str) -> str:
    parsed_url = urlparse(url)
    if parsed_url.fragment != '':
        return 'none'
    connection = HTTPSConnection(parsed_url.hostname)
    connection.request("GET", parsed_url.path)
    connection_response = connection.getresponse()
    if connection_response.status != 200:
        return 'none'
    connection_data = connection_response.read()
    return connection_data.decode()


def generate_absolute_links(host: str, relative_links: set[str]) -> set[str]:
    absolute_links = set()
    for relative_link in relative_links:
        absolute_links.add(urljoin(host, relative_link))
    return absolute_links


def count_word_on_page_and_subpages(url: str, word: str, visited_links=set()) -> int:
    count = 0
    html_data = fetch_html_data(url)
    if html_data == 'none':
        return count
    parser = CustomHTMLParser(word)
    parser.feed(html_data)
    count += parser.word_count
    sublinks = generate_absolute_links(url, parser.links_set)
    visited_links.add(url)
    print(url)
    if len(sublinks) == 0:
        return count
    for link in sublinks:
        if link in visited_links:
            continue
        count += count_word_on_page_and_subpages(link, word, visited_links)
    return count


def main():
    main_url = 'https://docs.python.org/3/library/urllib.parse.html'
    n = count_word_on_page_and_subpages(main_url, 'optional')
    print(n)
    print("Number of request: ", number_of_requests)


if __name__ == '__main__':
    yappi.start()
    main()
    func_stats = yappi.get_func_stats()
    func_stats.print_all()
    func_stats.save('yappi_output.pstats', 'PSTAT')
    func_stats.save('yappi_output.callgrid','CALLGRIND')
    yappi.stop()
    yappi.clear_stats()
