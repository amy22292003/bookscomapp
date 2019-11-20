"""A program to crawl and summarize the book data on books.com.

This program could crawl the book ranking data from the webpage:
https://www.books.com.tw/web/sys_tdrntb/books/
And summarize the category counts and get the top N percent discount books.

Usage :
    python booksapp.py [command]

    python booksapp.py all -n TOP_N [-f JSON_FILE]
    python booksapp.py category [-f JSON_FILE]
    python booksapp.py discount -n TOP_N [-f JSON_FILE]

Attributes:
    command: [all| category| discount]
        all: Complete all actions.
            (Crawling webpage, calculating the count of each category, and get top N percent books)
        category: Calculate the number of books in each level of categories.
        discount: Get top N percent of books that discount the most.
    TOP_N: Set the N percent
    JSON_FILE: The read/write JSON file path

"""

import argparse
import datetime
import sys
from pathlib import Path

import pandas as pd

import books_crawler


def category_count(filepath):
    """Calculating the number of books in each level of categories from a JSON file.

    Args:
        filepath (str): the JSON file path of book data

    Raises:
        FileNotFoundError: Raise if the JSON file doesn't exist.
    """

    try:
        # Check the file exists.
        file = Path(filepath)
        file.resolve(strict=True)

        # Get books from JSON file, and get the categories of books.
        df = pd.read_json(filepath)
        cate_df = df['category'].apply(pd.Series)

        # For each layer of category, calculate the count of each group.
        sys.stdout.write("=" * 10)
        sys.stdout.write(" Category ")
        sys.stdout.write("=" * 10 + "\n")
        top_group = cate_df.groupby([0]).size()
        # Print the first layer of category.
        sys.stdout.write(top_group.index[0] + " " + str(top_group.values[0]) + "\n")
        for layer in range(2, cate_df.shape[1] + 1):
            # Get the groups and their counts.
            groups = cate_df.groupby(list(range(layer))).size()
            group = ['>'.join(idx) + " " + str(groups[idx]) for idx in groups.index]
            sys.stdout.write(' | '.join(group) + "\n")

    except FileNotFoundError as e:
        sys.exit(e)
    except:
        raise


def most_discount_book(filepath, top_n):
    """Get top N percent of books that discount the most from a JSON file.

    Args:
        filepath (str): the JSON file path of book data
        top_n (int): the top_n percent

    Raises:
        FileNotFoundError: Raise if the JSON file doesn't exist.
        ValueError: Raise if top_n is not in the range 0 to 100.
    """

    try:
        # Check the file exists.
        file = Path(filepath)
        file.resolve(strict=True)

        # Check n in range 0 to 100
        if top_n > 100 or top_n < 0:
            raise ValueError("[Error] Top_N %i is not in range 0 to 100." % top_n)
        else:
            sys.stdout.write("=" * 10)
            sys.stdout.write(" Discount Book ")
            sys.stdout.write("=" * 10 + "\n")

            df = pd.read_json(filepath)
            n_num = round(df.shape[0] * (top_n / 100))  # Convert n percent to the number.
            n_row = df['discount_rate'].nsmallest(n_num, keep="all")  # Get n most discount books
            n_title = df.loc[list(n_row.index), 'title']
            sys.stdout.write("\n".join(n_title))
            sys.stdout.write("\n")

    except FileNotFoundError as e:
        sys.exit(e)
    except ValueError as e:
        sys.exit(e)
    except:
        raise


def _process_args():

    parser = argparse.ArgumentParser()
    subcmd = parser.add_subparsers(
        dest="subcmd", help="choose a action to take", metavar="command")
    subcmd.required = True

    all_parser = subcmd.add_parser("all", help="take the complete actions")
    all_parser.add_argument(
        "-f", dest="json_path", type=str, help="the JSON file path of books")
    all_parser.add_argument(
        "-n", dest="top_n", type=int, required=True, help="N percent most discount books")

    category_parser = subcmd.add_parser(
        "category", help="count number of books in each category")
    category_parser.add_argument(
        "-f", dest="json_path", type=str, help="the JSON file path of books")

    discount_parser = subcmd.add_parser(
        "discount", help="get most discount books")
    discount_parser.add_argument(
        "-f", dest="json_path", type=str, help="the JSON file path of books")
    discount_parser.add_argument(
        "-n", dest="top_n", type=int, required=True, help="N percent most discount books")

    return parser.parse_args()


def main():
    url = "https://www.books.com.tw/web/sys_tdrntb/books/"
    json_path = "books.json"

    args = _process_args()
    if args.json_path is not None:
        json_path = args.json_path

    # For different actions.
    if args.subcmd == "all":
        books_crawler.books_crawler(url, json_path)
        category_count(json_path)
        most_discount_book(json_path, args.top_n)
    elif args.subcmd == "category":
        category_count(json_path)
    elif args.subcmd == "discount":
        most_discount_book(json_path, args.top_n)


if __name__ == '__main__':
    main()