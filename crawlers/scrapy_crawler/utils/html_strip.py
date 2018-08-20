import re
from bs4 import BeautifulSoup

TAG_RE = re.compile(r'<[^>]+>')


def remove_tags(text):
    return TAG_RE.sub('', text)


def clear_content_full(content):
    soup = BeautifulSoup(content)
    for script in soup(['script', 'style']):
        script.extract()
    text = soup.get_text()
    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    return "\n".join(chunk for chunk in chunks if chunk)


def clear_content(content):
    soup = BeautifulSoup(content)
    for script in soup(['script', 'style']):
        script.extract()
    return soup.get_text()
