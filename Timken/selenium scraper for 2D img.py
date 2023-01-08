import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from time import sleep
import requests
from bs4 import BeautifulSoup
from random import randrange
from os import listdir
from os.path import isfile, join


def downloaded_pdf():

    downloads = r'C:\Users\olegk\Downloads'

    files = [f for f in listdir(downloads) if isfile(join(downloads, f))]

    pdfs = 0
    for file in files:
        if file.endswith(".pdf") and file.find('TheTimkenCompany') > 0:
            pdfs += 1
    return pdfs


def get_items_links(first_page_url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36'}
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


def save_pdfs(folder_name):
    downloads = r'C:\Users\olegk\Downloads'
    os.mkdir(downloads + "\\" + folder_name)
    files = [f for f in listdir(downloads) if isfile(join(downloads, f))]
    for file in files:
        if file.endswith(".pdf") and file.find('TheTimkenCompany') > 0:
            os.rename(downloads + "\\" + file,
                      downloads + "\\" + folder_name + "\\" + file[:file.find('-TheTimkenCompany')] + '.pdf')


def main():

    types = []

    os.environ['PATH'] += r"C:\SeleniumDrivers"

    with open('links.txt', 'r') as f:
        links_to_types = f.readlines()

    for idx, link_to_type in enumerate(links_to_types):
        types.append(get_items_links(link_to_type.replace('\n', '')))
        print(f"Scraping links {idx + 1} out of {len(links_to_types)}")

    for type_n, links_of_type in enumerate(types):

        for idx, link_to_item in enumerate(links_of_type):

            url = link_to_item.replace('\n', '')

            driver = webdriver.Chrome()

            driver.get(url)

            driver.fullscreen_window()

            element = driver.find_element(By.ID, 'SalesDrawing')

            element.click()

            element = driver.find_element(By.XPATH, '/html/body/div[18]/div[2]/form/table/tbody/tr[1]/td[2]/div/input')
            element.send_keys("olegkrivoruchko93@gmail.com")

            element = driver.find_element(By.XPATH, '/html/body/div[18]/div[2]/form/table/tbody/tr[2]/td[2]/div/input')
            element.send_keys("Oleg")

            element = driver.find_element(By.XPATH, '/html/body/div[18]/div[2]/form/table/tbody/tr[3]/td[2]/div/input')
            element.send_keys("Krivoruchko")

            element = driver.find_element(By.XPATH, '/html/body/div[18]/div[2]/form/table/tbody/tr[4]/td[2]/div/input')
            element.send_keys("AM")

            element = driver.find_element(By.XPATH, '/html/body/div[18]/div[2]/form/table/tbody/tr[6]/td[2]/div/select')
            element.send_keys("RUSSIAN FEDERATION")

            element = driver.find_element(By.XPATH, '/html/body/div[18]/div[2]/form/table/tbody/tr[7]/td[2]/div/input')
            element.send_keys("198095")

            element = driver.find_element(By.XPATH,
                                          '/html/body/div[18]/div[2]/form/div[2]/table/tbody/tr/td[1]/div/button')
            element.click()

            while not downloaded_pdf() == idx + 1:
                sleep(1)

            print(f"Downloading PDF {idx + 1} out of {len(links_of_type)}  type № {type_n + 1}")

            driver.close()

        save_pdfs(links_of_type[0].split('/')[-2])

if __name__ == '__main__':
    main()
