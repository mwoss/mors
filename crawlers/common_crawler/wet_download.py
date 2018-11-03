import logging
import os
from requests import get

from crawlers.common_crawler import directory_check

logging.basicConfig(format="%(asctime)s -- %(message)s", level=logging.INFO)


# TODO: Restrict downloading to n files and delete used urls from wet_list

class WetDownloader:
    """
    Class responsible for wet downloading 1-thread, non-asynchronous.
    For home-use(internet connection) it's the best choice.
    """

    def __init__(self):
        self.wet_list = 'data/path_files/wet.paths'
        self.dl_path = 'data/wet_data/'
        self.url_prefix = "https://commoncrawl.s3.amazonaws.com/"

    def run(self):
        directory_check(self.dl_path)

        with open(self.wet_list) as wet_urls:
            for url in wet_urls:
                url = url.strip()
                logging.info(f'Downloading file at url: {url}')
                self.__download_file(url)

    def __download_file(self, url: str):
        request_url = self.url_prefix + url
        request = get(request_url)
        logging.info(f'File {url} downloaded')

        extracted_name = url.split('/')[-1]
        with open(os.path.join(self.dl_path, extracted_name), 'wb') as c_file:
            c_file.write(request.content)
            logging.info(f'Saved file as: {extracted_name}')


if __name__ == '__main__':
    downloader = WetDownloader()
    downloader.run()
