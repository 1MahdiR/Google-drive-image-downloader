# GoogleDriveImageDownloader
# v1.1
#
# Download images from Google drive
#
# Script is available on github
# GITHUB: https://github.com/1MahdiR/Google-drive-image-downloader
#

import sys
import bs4
import re
from bs4 import BeautifulSoup
from requests import request
import multiprocessing
from selenium import webdriver
from time import sleep


def main(arg=None):

    # If no argument was specified
    if not arg:
        try:
            arg = input("Google drive image url: ")
        except KeyboardInterrupt:
            sys.exit(0)

    # Check if url is valid
    pattern = re.compile('http?s://drive.google.com/file/.*', flags=re.IGNORECASE)
    match = re.match(pattern, arg)

    # If this thread exit, script will raise an "connection timeout" error
    def time_out():
        sleep(90)

    def download_image(image_url):

        # options for web driver
        option = webdriver.FirefoxOptions()
        option.headless = True

        driver = webdriver.Firefox(options=option)
        driver.get(image_url)

        # parsing page source html
        while True:
            html = driver.page_source
            soup = BeautifulSoup(html, 'html.parser')

            tags_found = soup.find_all('img')
            if tags_found:
                tag = tags_found[0]
                break
            sleep(2)

        if tag:
            real_url = tag.attrs['src']
            # getting content
            response = request('get', url=real_url)
            if response.status_code == 200:
                with open('pic.jpg', 'wb') as f:
                    f.write(response.content)

    # If match was found
    if match:
        url = match.group()

        # Check if url returns 200
        res = request('get', url=url)
        if res.status_code == 404:
            raise Exception("Your file does not exist")
        elif res.status_code != 200:
            raise Exception("Your request was denied due to an unexpected error")

        # Downloading image thread
        t = multiprocessing.Process(target=download_image, args=(url,))

        # Timer thread
        timer = multiprocessing.Process(target=time_out)

        t.start()
        timer.start()

        try:
            while True:
                print("  Downloading... /\r", end="")
                sleep(0.2)
                print("  Downloading... -\r", end="")
                sleep(0.2)
                print("  Downloading... \\\r", end="")
                sleep(0.2)
                print("  Downloading... |\r", end="")

                if not timer.is_alive():
                    t.terminate()
                    raise Exception("Connection Timeout")

                # If downloading was successful
                if not t.is_alive():
                    timer.terminate()
                    print()
                    sys.exit(0)

        except KeyboardInterrupt:
            t.terminate()
            timer.terminate()
            print()
            sys.exit(0)

        except Exception as e:
            print(e)
            t.terminate()
            timer.terminate()
            print()
            sys.exit(2)

    else:
        raise Exception("Unexpected url\n")


if __name__ == '__main__':
    if len(sys.argv) > 1:
        main(sys.argv[1])
    else:
        main()
