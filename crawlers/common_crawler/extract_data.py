import logging
from concurrent.futures import ProcessPoolExecutor
from glob import iglob
from json import dumps
from os import remove, path
from re import compile, sub
from typing import Generator

from langdetect import detect
from langdetect.lang_detect_exception import LangDetectException
from warc import WARCRecord, open as warc_open

from crawlers.common_crawler import directory_check

logging.basicConfig(format="%(asctime)s -- %(message)s", level=logging.INFO)


class WETDataExtractor:
    """
    Extractor for retrieving english record from WET files.
    """
    FID_REGEX = compile(r'.*:(.*)>')

    def __init__(self):
        self.wet_path = 'data/wet_data2/'
        self.record_path = 'data/records2/'
        self.max_workers = 4

    def extract(self):
        directory_check(self.record_path)

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            for file_path in iglob(path.join(self.wet_path, '*')):
                record_generator = self.get_warc_file(file_path)
                executor.map(self._process_record, record_generator)
                logging.info(f'File: {file_path} extracted')

                self._delete_warc_file(file_path)

    def get_warc_file(self, file_path: str) -> Generator[WARCRecord, None, None]:
        with warc_open(file_path) as f:
            for record in f:
                record.payload = record.payload.read()
                yield record

    def _process_record(self, record: WARCRecord):
        if record.header.content_length < 500:
            logging.warning('Record too short skipping')
            return

        byte_data: bytes = record.payload
        text = self._normalize(byte_data.decode('utf-8'))

        try:
            lang_det = detect(text[:250])
            if lang_det == 'en':
                fid = self.FID_REGEX.match(record.header.record_id)[1]
                self._save2file(fid, record.url, text)
        except LangDetectException:
            logging.warning('Cannot detect language. Skipping record')

    def _save2file(self, fid, url, content):
        file_name = fid + '.json'
        with open(path.join(self.record_path, file_name), 'w', encoding='utf-8') as f:
            f.write(dumps({
                'url': url,
                'content': content
            }, ensure_ascii=False))

    @staticmethod
    def _normalize(text: str) -> str:
        clear_lines = (sub('\W+', ' ', line) for line in text.splitlines() if len(line) > 65)
        return '\n'.join(clear_lines)

    @staticmethod
    def _delete_warc_file(file_path: str):
        try:
            remove(file_path)
        except OSError as err:
            logging.error(err)


if __name__ == '__main__':
    extractor = WETDataExtractor()
    extractor.extract()
