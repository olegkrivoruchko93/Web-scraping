import requests
from bs4 import BeautifulSoup
from time import sleep
import xlsxwriter
from random import randrange
import os


def get_items_links(first_page_url):

    items_links = []
    page_num = 1

    link = first_page_url + f"&pagenum={page_num}"
    html_doc = BeautifulSoup(requests.get(link, headers=headers).text, 'html.parser')

    tags = html_doc.find_all("a", class_='plp-itemlink')

    for item in tags:
        items_links.append("https://cad.timken.com" + item.get('href'))

    page_num += 1

    while html_doc.prettify().lower().find(f'pagenum={page_num}') > 0:

        link = first_page_url + f"&pagenum={page_num}"

        html_doc = BeautifulSoup(requests.get(link, headers=headers).text, 'html.parser')

        tags = html_doc.find_all("a", class_='plp-itemlink')

        for item in tags:
            items_links.append("https://cad.timken.com" + item.get('href'))

        page_num += 1
        sleep(randrange(3, 6))

    return items_links


def main():

    types = []

    with open('links.txt', 'r') as f:
        links_to_types = f.readlines()

    for idx, link_to_type in enumerate(links_to_types):
        types.append(get_items_links(link_to_type.replace('\n', '')))
        print(f"Scraping links {idx + 1} out of {len(links_to_types)}")

    for type_n, links_of_type in enumerate(types):

        folder_name = links_of_type[0].split('/')[-2]
        os.mkdir(folder_name)

        with xlsxwriter.Workbook(f'{folder_name}\{folder_name}.xlsx') as workbook:
            worksheet1 = workbook.add_worksheet()

            items = []
            url_to_images = []
            col_names = []
            links_of_type_len = len(links_of_type)

            for idx, link_to_item in enumerate(links_of_type):

                print("{0:.2%} of parsing".format((idx + 1) / links_of_type_len) + f" type № {type_n + 1} link: {link_to_item}")

                item = dict()

                item['link'] = link_to_item
                item['url'] = link_to_item.split('/')[-1]

                # making few tries if failed to connect, so i don't crash
                tries = 1
                while tries < 6:
                    try:
                        html_doc = BeautifulSoup(requests.get(link_to_item, headers=headers).text, 'html.parser')
                        break
                    except:
                        sleep(tries * 60)
                        tries += 1
                        pass

                html_doc = BeautifulSoup(requests.get(link_to_item, headers=headers).text, 'html.parser')

                item['art'] = html_doc.find("span", itemprop="sku").text

                specs = html_doc.find_all(itemprop="additionalProperty")

                for spec in specs:

                    # So footnote don't get in list
                    tag_with_name = spec.find("td", class_="plp-table-name left")
                    if tag_with_name is None:
                        continue
                    else:
                        name = tag_with_name.text.replace('\n', '')

                    values = spec.find_all("span")

                    value = ""
                    for i in values:
                        if 'data-measure' in i.attrs and (
                                i.attrs['data-measure'] == 'general' or i.attrs['data-measure'] == 'metric'):
                            value = i.text

                    item[name] = value

                images_of_item = []
                for link in html_doc.find_all('a'):
                    link_to_image = link.get('href')
                    if isinstance(link_to_image, str) and link_to_image.find(r'/Asset') == 0 and link_to_image.find(
                            r'jpg') > 0:
                        url_to_images.append('https://cad.timken.com' + link_to_image)
                        images_of_item.append(link_to_image.split('/')[-1])

                item['images'] = ", ".join(images_of_item)

                items.append(item)

                sleep(randrange(3, 6))

            items_len = len(items)
            for idx, item in enumerate(items):
                for name in item.keys():
                    col_names.append(name)
                print("{0:.2%} of adding col names".format((idx + 1) / links_of_type_len) + f" type № {items_len}")

            col_names = list(set(col_names))  # back to list so I have an index

            col_names.insert(0, col_names.pop(col_names.index("art")))
            col_names.insert(0, col_names.pop(col_names.index("url")))
            col_names.insert(0, col_names.pop(col_names.index("link")))
            col_names.insert(len(col_names) - 1, col_names.pop(col_names.index("images")))

            for idx, col_name in enumerate(col_names):
                worksheet1.write(0, idx, col_name)

            for idx, item in enumerate(items):
                for key in item:
                    col_num = col_names.index(key)
                    worksheet1.write(idx + 1, col_num, item[key])
                print("{0:.2%} of writing to excel".format((idx + 1) / links_of_type_len) + f" {type_n + 1}")

            os.mkdir(f'{folder_name}\img')

            url_to_images = set(url_to_images)

            url_to_images_len = len(url_to_images)

            for idx, url in enumerate(url_to_images):
                page = requests.get(url, headers=headers)
                out = open(f'{folder_name}\img\{url.split("/")[-1]}', "wb")
                out.write(page.content)
                out.close()
                sleep(randrange(3, 6))
                print("{0:.2%} downloading images".format((idx + 1) / url_to_images_len) + f" type № {type_n + 1}")

            print(f'finished {type_n + 1} file')


if __name__ == '__main__':
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
    main()
