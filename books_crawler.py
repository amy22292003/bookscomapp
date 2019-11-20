import json
import os
import requests

from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def _get_session():
    session = requests.Session()
    retry = Retry(backoff_factor=1, status_forcelist=[404, 408])
    session.mount('http://', HTTPAdapter(max_retries=retry))
    session.mount('https://', HTTPAdapter(max_retries=retry))

    return session


def _get_soup(url, session):
    ua = UserAgent()
    headers = {'User-Agent': str(ua.random)}

    resp = session.get(url, headers=headers)
    resp.raise_for_status()

    return BeautifulSoup(resp.text, 'html.parser')


def _get_bookdata(rank, soup, session):
    """Get details of a book by url and given soup object.

    Args:
        rank (int): The rank of a book.
        url (str): The url of a book detail page.
        session: Connection session for requesting the url.
    Returns:
        book (dict): A book with related information(title, author, price...).
    """

    title = soup.h4.string
    author = soup.find('ul', class_='msg').a.string

    price_soup = soup.find('li', class_='price_a')
    discount_price = int(price_soup.find_all('b')[-1].string)
    discount_rate = None
    # If there is a discount.
    if len(price_soup.find_all('b')) > 1:
        discount_rate = int(price_soup.find('b').string)

    # Get category and list price from the book detail page.
    book_url = soup.a['href']
    book_soup = _get_soup(book_url, session)
    category = None
    price = None
    # If the detail page can be accessed without login
    if book_soup.find('ul', class_='type04_breadcrumb') is not None:
        cate_soup = book_soup.find('ul', class_='type04_breadcrumb').find_all('span')
        category = [s.string for s in cate_soup][:-1]
        if discount_rate is not None:  # If there is a discount, get the list price
            price = int(book_soup.find('ul', class_='price').em.string)
    else:
        print('The book:', title, ' needing login to view.')

    book = {
        'rank': rank,
        'title': title,
        'author': author,
        'discount_price': discount_price,
        'price': price,
        'discount_rate': discount_rate,
        'category': category
    }

    return book


def _save_jsonfile(book_list, filepath):
    if os.path.dirname(filepath) != "":
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(book_list, f, ensure_ascii=False)

def books_crawler(url, filepath):
    """Crawl the book detail on the given url, and save data to JSON file.

    Args:
        url (str): The url of books.com sys_tdrntb page.
        filepath: the JSON file path that will be used to save book detail.
    """

    session = _get_session()
    soup = _get_soup(url, session)  # Get the sys_tdrntb page
    all_soup = soup.find_all('li', class_='item')  # Get all book elements.

    book_list = []
    # Get book detail for each book
    for i, a_soup in enumerate(all_soup, start=1):
        # Renew session for every 10 books
        if i % 10 == 0:
            print('Crawling ', i, '... books...')
            session = _get_session()
        # Get data of a book
        book = _get_bookdata(i, a_soup, session)
        book_list.append(book)

    print("Completing crawling the pages...")
    _save_jsonfile(book_list, filepath)