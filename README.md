# books
This is a program to crawl and summarize the book data on books.com.

It crawl the book ranking data from the webpage:
https://www.books.com.tw/web/sys_tdrntb/books/
Then it calculate the number of books in each level of categories of books.
And it get the top N percent of books that discount the most.

## Requirements
* Python3.6 (Tested on 3.6.9)
* Beautifulsoup4 (Tested on 4.8.1)
* Requests (Tested on 2.22.0)
* Pandas (Tested on 0.25.3)
* fake_useragent (Tested on 0.1.11)

## Build environment
Recommend using Anaconda to set up the python 3.6 environment
'''
$ conda create --name myenv python=3.6
'''

## Usage
There are 3 functions: all, category, discount
'''
python booksapp.py COMMAND -n TOP_N -f JSON_FILE
'''

1. all
Complete all actions.
Crawling webpage, calculating the count of each category, and getting top N percent books.
'''
python booksapp.py all -n TOP_N [-f JSON_FILE]
'''
TOP_N: the top N percent of books
JSON_FILE (optional, default:"./books.json"): set the read/write JSON file path of book detail

2. category
Calculate the number of books in each level of categories from a JSON file.
'''
python booksapp.py category [-f JSON_FILE]
'''
JSON_FILE (optional, default:"./books.json"): set the JSON file path of book detail

3. discount
Get top N percent of books that discount the most from a JSON file.
'''
python booksapp.py discount -n TOP_N [-f JSON_FILE]
'''
TOP_N: the top N percent of books
JSON_FILE (optional, default:"./books.json"): set the JSON file path of book detail

Example:
'''
python booksapp.py all -n 3 -f test.json
python booksapp.py category
python booksapp.py discount -n 3
'''