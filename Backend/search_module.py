from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import json
import pandas as pd
from newspaper import Article, article, ArticleException, ArticleBinaryDataException
import time
import datetime
import random
from time import sleep
from bs4 import BeautifulSoup
from requests import get
from urllib.parse import unquote # to decode the url
import string
import unicodedata
import re
import pandas as pd
import numpy as np
import numpy as np

from is_testing import OFFLINE_TESTING

def get_useragent():
    """
    Generates a random user agent string mimicking the format of various software versions.

    The user agent string is composed of:
    - Lynx version: Lynx/x.y.z where x is 2-3, y is 8-9, and z is 0-2
    - libwww version: libwww-FM/x.y where x is 2-3 and y is 13-15
    - SSL-MM version: SSL-MM/x.y where x is 1-2 and y is 3-5
    - OpenSSL version: OpenSSL/x.y.z where x is 1-3, y is 0-4, and z is 0-9

    Returns:
        str: A randomly generated user agent string.
    """
    #return "Mozilla/5.0 (X11; Linux x86_64; rv:134.0) Gecko/20100101 Firefox/134.0"
    lynx_version = f"Lynx/{random.randint(2, 3)}.{random.randint(8, 9)}.{random.randint(0, 2)}"
    libwww_version = f"libwww-FM/{random.randint(2, 3)}.{random.randint(13, 15)}"
    ssl_mm_version = f"SSL-MM/{random.randint(1, 2)}.{random.randint(3, 5)}"
    openssl_version = f"OpenSSL/{random.randint(1, 3)}.{random.randint(0, 4)}.{random.randint(0, 9)}"
    return f"{lynx_version} {libwww_version} {ssl_mm_version} {openssl_version}"

google_abuse_ex = 'ID=3b4acdbf8e1d4cd0:TM=1743624317:C=r:IP=141.85.144.110-:S=OhVppR_3S_782NrjQ5-gLyo'
def _req(term, results, lang, start, proxies, timeout, safe, ssl_verify, region):
    resp = get(
        url="https://www.google.com/search",
        headers={
            "User-Agent": get_useragent(),
            "Accept": "*/*"
        },
        params={
            "q": term,
            "num": results + 2,  # Prevents multiple requests
            "hl": lang,
            "start": start,
            "safe": safe,
            "gl": region,
        },
        proxies=proxies,
        timeout=timeout,
        verify=ssl_verify,
        cookies = {
            'CONSENT': 'PENDING+987', # Bypasses the consent page
            'SOCS': 'CAESHAgCEhJnd3NfMjAyNTAzMjctMF9SQzMaAmVuIAEaBgiA_LG_Bg',
            'DV' : 'w3S-XcBZhSMfoLzqnEwKQNAh2UuKXxk',
            'AEC': 'AVcja2e1ySUjdOhfTHhkM6Et-jccybyi_PU8RK3Acg8lzpFoWcSYITptRg',
            #'GOOGLE_ABUSE_EXEMPTION': google_abuse_ex,
            #'__Secure-ENID': secure_enid,
        }
    )
    resp.raise_for_status()
    return resp


class SearchResult:
    def __init__(self, url, title, description):
        self.url = url
        self.title = title
        self.description = description

    def __repr__(self):
        return f"SearchResult(url={self.url}, title={self.title}, description={self.description})"


def search(term, num_results=10, lang="en", proxy=None, advanced=False, sleep_interval=0, timeout=5, safe="active", ssl_verify=None, region=None, start_num=0, unique=False):
    """Search the Google search engine"""

    if OFFLINE_TESTING:
        print("Detected offline testing.")
        yield "https://www.digi24.ro/stiri/actualitate/politica/nicusor-dan-a-vorbit-la-telefon-cu-donald-trump-3259103"
        yield "https://hotnews.ro/nicusor-dan-confirma-oficial-ca-a-vorbit-cu-donald-trump-i-am-multumit-pentru-1988043"
        yield "https://romania.europalibera.org/a/donald-trump-nicusor-dan-convorbire-telefonica-invitatie-in-sua/33427238.html"
        yield "https://hotnews.ro/nicusor-dan-confirma-oficial-ca-a-vorbit-cu-donald-trump-i-am-multumit-pentru-1988043"
        return

    # Proxy setup
    proxies = {"https": proxy, "http": proxy} if proxy and (proxy.startswith("https") or proxy.startswith("http") or proxy.startswith("socks5")) else None

    start = start_num
    fetched_results = 0  # Keep track of the total fetched results
    fetched_links = set() # to keep track of links that are already seen previously

    while fetched_results < num_results:
        # Send request
        resp = _req(term, num_results - start,
                    lang, start, proxies, timeout, safe, ssl_verify, region)
        
        # put in file - comment for debugging purpose
        with open('google.html', 'w') as f:
            f.write(resp.text)
        
        # Parse
        soup = BeautifulSoup(resp.text, "html.parser")
        result_block = soup.find_all("div", class_="ezO2md")
        new_results = 0  # Keep track of new results in this iteration

        for result in result_block:
            # Find the link tag within the result block
            link_tag = result.find("a", class_="fuLhoc", href=True)
            # Find the title tag within the link tag
            title_tag = link_tag.find("span", class_="dXDvrc") if link_tag else None

            # Check if all necessary tags are found
            if not (link_tag and title_tag):
                # Extract and decode the link URL
                continue
            # Extract and decode the link URL
            link = unquote(link_tag["href"].split("&")[0].replace("/url?q=", "")) if link_tag else ""
            # Check if the link has already been fetched and if unique results are required
            if link in fetched_links and unique:
                continue  # Skip this result if the link is not unique
            # Add the link to the set of fetched links
            fetched_links.add(link)
            # Extract the title text
            title = title_tag.text if title_tag else ""
            # Extract the description text
            description = ""
            # Increment the count of fetched results
            fetched_results += 1
            # Increment the count of new results in this iteration
            new_results += 1
            # Yield the result based on the advanced flag
            if advanced:
                yield SearchResult(link, title, description)  # Yield a SearchResult object
            else:
                yield link  # Yield only the link

            if fetched_results >= num_results:
                break  # Stop if we have fetched the desired number of results

        if new_results == 0:
            #If you want to have printed to your screen that the desired amount of queries can not been fulfilled, uncomment the line below:
            #print(f"Only {fetched_results} results found for query requiring {num_results} results. Moving on to the next query.")
            break  # Break the loop if no new results were found in this iteration

        start += 10  # Prepare for the next set of results
        sleep(sleep_interval)
