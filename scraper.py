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
    return [number for heading, number, reader in columns]


def get_column_headings(columns, heading_row):
    th_selector = nth_css_selectors('th', column_numbers(columns))
    th_tags = heading_row.select(th_selector)
    return [th_tag.text for th_tag in th_tags] 


def get_column_values(columns, row):
    def read_tag(i, tag):
        heading, number, reader = columns[i]
        return reader(tag)

    td_tags = row.select(nth_css_selectors('td', column_numbers(columns)))
    return [read_tag(i, td_tag) for i, td_tag in enumerate(td_tags)]


def get_data_frame(columns, heading_row, content_rows):
    headings = get_column_headings(columns, heading_row)
    data = [get_column_values(columns, row) for row in content_rows]
    return pandas.DataFrame(data, columns=headings)


def parse_page(html, page_name, table_id):
    columns = PAGE_COLUMNS[page_name]
    heading_row, content_rows = get_table_headings_and_contents(html, table_id)
    return get_data_frame(columns, heading_row, content_rows)


PAGE_COLUMNS = {
    'exchanges': [
        ('Name', 2, attr('data-sort')),
        ('Adj. Vol (24h)', 3, attr('data-sort')),
        ('Volume (24h)', 4, attr('data-sort')),
        ('Volume (7d)', 5, attr('data-sort')),
        ('Volume (30d)', 6, attr('data-sort')),
        ('No. Markets', 7, attr('data-sort')),
        ('Change (24h)', 10, attr('data-sort')),
    ],
    'exchange_coins': [
        ('Currency', 2, attr('data-sort')),
        ('Pair', 3, attr('data-sort')),
        ('Volume (24h)', 4, child('span', 'data-btc')),
        ('Price', 5, attr('data-sort')),
        ('Volume (%)', 6, attr('data-sort')),
    ]
}


if __name__ == '__main__':
    url = 'https://coinmarketcap.com/rankings/exchanges/'
    with urllib.request.urlopen(url) as response:
        print(parse_page(response.read(), 'exchanges', '#exchange-rankings'))

    exchanges = ['binance']
    url_template = 'https://coinmarketcap.com/exchanges/%s/#markets'
    pages = dict([(exchange, url_template % exchange) for exchange in exchanges])
    for exchange, url in pages.items():
        with urllib.request.urlopen(url) as response:
            print()
            print('--- Coins for %s ---' % exchange)
            print(parse_page(response.read(), 'exchange_coins', '#exchange-markets'))
