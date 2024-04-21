import os
import shutil
from bs4 import BeautifulSoup as bs
from lxml import etree
import re
from Crypto.Cipher import AES
import base64
import requests
import magic
import cloudscraper


def get_encrypted_imgsrcs(url: str) -> str:
    scraper = cloudscraper.create_scraper()
    return re.search(r"imgsrcs = '(.*)'", scraper.get(url).text).group(1)


def decrypt_imgsrcs(imgsrcs: str) -> list[str]:
    key = bytes.fromhex('e11adc3949ba59abbe56e057f20f883e')
    iv = bytes.fromhex('1234567890abcdef1234567890abcdef')
    cipher = AES.new(key, AES.MODE_CBC, iv)
    decrypted = cipher.decrypt(base64.b64decode(imgsrcs)).decode('utf-8')
    decrypted = decrypted[:-5]
    return decrypted.split(",")


def download_imgs(imgsrcs: list[str]) -> None:
    save_folder = os.getcwd() + "\\output"
    if os.path.exists(save_folder):
        shutil.rmtree(save_folder)
    os.makedirs(save_folder)

    for index, img_link in enumerate(imgsrcs, start=1):
        r = requests.get(img_link)
        file_ext = magic.from_buffer(r.content, mime=True).split("/")[1]
        with open(f"{save_folder}\\{index}.{file_ext}", "wb") as f:
            f.write(r.content)
        print(f"[INFO] {index}/{len(imgsrcs)}")


def main(url: str) -> None:
    url = re.search(r'^(.*?)(?=\bpg\b)', url).group(1)+"pg-1/"
    imgsrcs = decrypt_imgsrcs(get_encrypted_imgsrcs(url))
    download_imgs(imgsrcs)


if __name__ == "__main__":
    import sys
    correct_url = ""
    while not correct_url:
        if len(sys.argv) > 1:
            url = sys.argv[1]
        else:
            url = input("Enter chapter url: ")
        match = re.search(r'https://www.mangago.me/read-manga/(.*)/(.*)/(.*)/(.*)/(.*)', url)
        if match:
            correct_url = url
            main(url)
            break
        print("[ERROR] Url isn't supported")

