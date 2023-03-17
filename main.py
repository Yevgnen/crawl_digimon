# -*- coding: utf-8 -*-

import itertools
import os

import filefox
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
    image_urls = itertools.chain(
        (x.get("href") for x in root.xpath("//div[contains(@class, 'digimon_img')]/a")),
        (
            x.get("src")
            for x in root.xpath("//div[contains(@class, 'digimon_img')]//img")
        ),
    )
    for path in image_urls:
        image_file = os.path.join(image_dir, path)
        if not os.path.exists(image_file):
            url = os.path.join(BASE_URL, name, path)
            get_image(url, image_file)


def parse_html(html):
    def parse_basic_info(e):
        keys = [x.text for x in e.xpath("./table//th")]
        values = [x.text for x in e.xpath("./table//td")]

        return dict(zip(keys, values))

    root = etree.fromstring(html, etree.HTMLParser())
    article = root.xpath("//article")[0]

    elements = {}
    it = iter(article.iterchildren())
    while (child := next(it, None)) is not None:
        if child.tag == "h3":
            elements[child.text] = next(it, None)

    value = {}
    for key, element in elements.items():
        if key == "基本资料":
            value = parse_basic_info(element)

    return value


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

        with open(html_file) as f:
            data = parse_html(f.read())
        json_file = os.path.join(dirname, "data.json")
        filefox.write_json(data, json_file, ensure_ascii=False, indent=4)


if __name__ == "__main__":
    main()
