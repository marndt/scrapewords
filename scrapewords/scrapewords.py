from bs4 import BeautifulSoup
import json
import re
import requests
import sys
import unicodedata
import urlparse

# Characters to strip (punctuation)
SC = u"".join([unichr(i) for i in xrange(sys.maxunicode) if unicodedata.category(unichr(i)).startswith('P')])


def is_valid(word):
    # Throw out long "word" strings and run-ons
    stripped_word = word.strip(SC)
    if len(stripped_word) > 25 or len(stripped_word) < 1:
        return False
    # Throw out "words" with no alpha characters
    if not re.search(r'[A-z]', word):
        return False
    return True


def scrape_source(source_url):
    source = {
        'source': source_url,
        'h1': [],
        'h2': [],
        'h3': [],
        'h4': [],
        'h5': [],
        'h6': [],
        'other': [],
        'a': {},
    }

    try:
        r = requests.get(source_url, timeout=5)
    except requests.exceptions.RequestException:
        # If the URL doesn't load, just return the empty structure
        return source

    soup = BeautifulSoup(r.text, "html.parser")

    for el in soup.findAll('style'):
        el.extract()
    for el in soup.findAll('script'):
        el.extract()

    # We'll throw all the words in the document into other and then remove the ones
    # that appear in more specific elements as we go
    source['other'] = [word.strip(SC) for word in " ".join(soup.stripped_strings).split() if is_valid(word)]

    for eltype in ('h1', 'h2', 'h3', 'h4', 'h5', 'h6'):
        for el in soup.findAll(eltype):
            # Only using the first 10 words in an <hX>
            # This covers 99% of <hX> tags and avoids problems like a whole document being inside the <hX> tag
            for word in " ".join(el.stripped_strings).split()[:10]:
                if is_valid(word):
                    source[eltype].append(word.strip(SC))
                    try:
                        source['other'].remove(word.strip(SC))
                    except ValueError:
                        if el.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                            pass
                        elif el.parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                            pass

    for el in soup.findAll('a', href=True):
        if not el['href'].startswith('http'):
            continue

        try:
            netloc = urlparse.urlparse(el['href']).netloc
        except ValueError:
            continue

        url_path = urlparse.urlparse(el['href']).path
        base_domain = '.'.join(netloc.split('.')[-2:])

        if base_domain not in source['a']:
            source['a'][base_domain] = {}

        if netloc not in source['a'][base_domain]:
            source['a'][base_domain][netloc] = []

        anchortext = []
        # Only using the first 10 words in an <a>
        for word in " ".join(el.stripped_strings).split()[:10]:
            if is_valid(word):
                try:
                    source['other'].remove(word.strip(SC))
                except ValueError:
                    if el.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6']):
                        pass
                    elif el.parent.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        pass
                    else:
                        pass
                anchortext.append(word.strip(SC))

        linkwords = [word for word in re.findall(r"\w+", url_path) if is_valid(word)]

        source['a'][base_domain][netloc].append({
            'linkwords': linkwords,
            'anchortext': anchortext,
        })

    return source


def scrapewords():
    if len(sys.argv) < 3:
        sys.stdout.write("usage: {0} <input_file> <output_file>\n".format(sys.argv[0]))
        exit()
    infile = open(sys.argv[1])
    outfile = open(sys.argv[2], 'w')

    urls = []
    for line in infile:
        if line.strip() == 'link':
            continue
        urls.append(line.decode('iso8859').strip())

    outfile.write("[")
    for i, url in enumerate(urls):
        if i > 0:
            outfile.write(",")
        sys.stdout.write(u"\r[{0}/{1}] {2}".format(i + 1, len(urls), url)[:80].ljust(80))
        sys.stdout.flush()
        outfile.write(json.dumps(scrape_source(url)))
    sys.stdout.write("\n")
    outfile.write("]")

if __name__ == "__main__":
    scrapewords()
