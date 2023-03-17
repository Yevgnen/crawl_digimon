# -*- coding: utf-8 -*-

import os

import requests
import tqdm
from lxml import etree

BASE_URL = "http://digimons.net/digimon/"


def get_page(url, filename):
    content = requests.get(url).content.decode()
    with open(filename, mode="w") as f:
        f.writelines(content)


def get_image(url, filename):
    resp = requests.get(url)
    with open(filename, mode="wb") as f:
        f.write(resp.content)


def get_index_urls():
    index_url = os.path.join(BASE_URL, "sort.html")
    resp = requests.get(index_url)
    root = etree.fromstring(resp.content.decode(), etree.HTMLParser())

    urls = {}
    for url in root.xpath("//td/a[contains(@href, 'index')]"):
        url = url.get("href")
        name = url.split("/")[0]
        urls[name] = os.path.join(BASE_URL, url)

    return urls


def get_images(name, html_file, image_dir):
    with open(html_file) as f:
        content = f.read()

    os.makedirs(image_dir, exist_ok=True)

    root = etree.fromstring(content, etree.HTMLParser())
    for element in root.xpath("//div[contains(@class, 'digimon_img')]/a"):
        path = element.get("href")

        image_file = os.path.join(image_dir, path)
        if not os.path.exists(image_file):
            url = os.path.join(BASE_URL, name, path)
            get_image(url, image_file)


def main():
    output_dir = "output/"
    os.makedirs(output_dir, exist_ok=True)

    urls = get_index_urls()
    for name, url in tqdm.tqdm(urls.items()):
        dirname = os.path.join(output_dir, name)
        os.makedirs(dirname, exist_ok=True)
        html_file = os.path.join(dirname, "index.html")
        if not os.path.exists(html_file):
            get_page(url, html_file)

        image_dir = os.path.join(dirname, "images")
        get_images(name, html_file, image_dir)


if __name__ == "__main__":
    main()
