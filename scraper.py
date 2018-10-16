import urllib

import bs4
import pandas


def nth_css_selectors(tag_name, numbers):
    return ', '.join(['%s:nth-of-type(%s)' % (tag_name, n) for n in numbers])


def attr(name):
    return lambda tag: tag[name]


def child(tag_name, attr_name):
    return lambda tag: getattr(tag, tag_name)[attr_name]


def get_table_headings_and_contents(html, table_id):
    parser = bs4.BeautifulSoup(html, features='html.parser')
    table = parser.select(table_id)[0]
    heading_row, *content_rows = table('tr')
    return heading_row, content_rows


def column_numbers(columns):
    return [number for number, reader in columns]


def get_column_headings(columns, heading_row):
    th_selector = nth_css_selectors('th', column_numbers(columns))
    th_tags = heading_row.select(th_selector)
    return [th_tag.text for th_tag in th_tags] 


def get_column_values(columns, row):
    def read_tag(i, tag):
        return columns[i][1](tag)

    td_tags = row.select(nth_css_selectors('td', column_numbers(columns)))
    return [read_tag(i, td_tag) for i, td_tag in enumerate(td_tags)]


def get_data_frame(columns, heading_row, content_rows):
    headings = get_column_headings(columns, heading_row)
    data = [get_column_values(columns, row) for row in content_rows]
    return pandas.DataFrame(data, columns=headings)


def extract_exchanges(html):
    table_id = '#exchange-rankings'
    heading_row, content_rows = get_table_headings_and_contents(html, table_id)

    columns = [
        (2, attr('data-sort')),
        (3, attr('data-sort')),
        (4, attr('data-sort')),
        (5, attr('data-sort')),
        (6, attr('data-sort')),
        (7, attr('data-sort')),
        (10, attr('data-sort')),
    ]

    return get_data_frame(columns, heading_row, content_rows)


def extract_coin(html):
    table_id = '#exchange-markets'
    heading_row, content_rows = get_table_headings_and_contents(html, table_id)

    columns = [
        (2, attr('data-sort')),
        (3, attr('data-sort')),
        (4, child('span', 'data-btc')),
        (5, attr('data-sort')),
        (6, attr('data-sort')),
    ]

    return get_data_frame(columns, heading_row, content_rows)


if __name__ == '__main__':
    url = 'https://coinmarketcap.com/rankings/exchanges/'
    with urllib.request.urlopen(url) as response:
        print(extract_exchanges(response.read()))

    exchanges = ['binance']
    url_template = 'https://coinmarketcap.com/exchanges/%s/#markets'
    pages = dict([(exchange, url_template % exchange) for exchange in exchanges])
    for exchange, url in pages.items():
        with urllib.request.urlopen(url) as response:
            print(extract_coin(response.read()))
            print()
            print('--- Coins for %s ---' % exchange)
