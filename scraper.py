import bs4
import pandas


def nth_css_selectors(tag_name, numbers):
    return ', '.join(['%s:nth-of-type(%s)' % (tag_name, n) for n in numbers])


def attr(name):
    return lambda tag: tag[name]


def extract_exchanges(html):
    parser = bs4.BeautifulSoup(html, features='html.parser')
    cells = []

    table = parser.select('#exchange-rankings')[0]

    columns = [
        (2, attr('data-sort')),
        (3, attr('data-sort')),
        (4, attr('data-sort')),
        (5, attr('data-sort')),
        (6, attr('data-sort')),
        (7, attr('data-sort')),
        (10, attr('data-sort')),
    ]

    column_numbers = [number for number, reader in columns]

    heading_row, *content_rows = table('tr')

    # Extract column headings
    th_tags = heading_row.select(nth_css_selectors('th', column_numbers))
    headings = [th_tag.text for th_tag in th_tags]

    # Extract contents of table
    def read_tag(i, tag):
        return columns[i][1](tag)

    data = []
    for row in content_rows:
        td_tags = row.select(nth_css_selectors('td', column_numbers))
        data.append([read_tag(i, td_tag) for i, td_tag in enumerate(td_tags)])

    return pandas.DataFrame(data, columns=headings)


if __name__ == '__main__':
    with open('exchanges.html') as f:
        print(extract_exchanges(f.read()))
