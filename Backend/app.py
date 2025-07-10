from flask import Flask
from flask import request
from flask_cors import CORS, cross_origin
import json
import pandas as pd
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
from newspaper import Article, ArticleException, ArticleBinaryDataException
from pickle import load

from search_module import search, SearchResult

from models import get_query, check_match, get_report

from is_testing import OFFLINE_TESTING, REPORT_ENABLED

domain_regex = "^.*:\\/\\/((www\\.)?.*\\.[a-z]{2,4})[\\/\\?].*$"


if not OFFLINE_TESTING:
    from newspaper import article
else:
    CURRENT_ARTICLE_NUMBER = 0
    ARTICLE_NUMBER = 4

    def article(input):
        global CURRENT_ARTICLE_NUMBER, ARTICLE_NUMBER
        with open(f'test_article{CURRENT_ARTICLE_NUMBER}.pickle', 'rb') as f:
            data = load(f)
        
        CURRENT_ARTICLE_NUMBER = (CURRENT_ARTICLE_NUMBER + 1 ) % ARTICLE_NUMBER
        
        return data

        

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return "<p>Hello, World!</p>"

def filter_query_string(query_string):
    to_remove_list = ["</s>"]

    filtered_string = query_string

    for el in to_remove_list:
        filtered_string = filtered_string.replace(el, "").replace("  ", " ").strip()
    
    return filtered_string

@app.route("/search_similar", methods=["POST"])
def search_similar():

    try:
        input_article = request.get_json()["article_link"]
        
        print("Got the input article:", input_article)

        fetched_article = article(input_article)

        if not fetched_article.text:
            return {
            "error": "Cannot process the article."
            }

        domain_regex_run = re.search(domain_regex, input_article)
        input_domain = domain_regex_run.group(1)

        generated_query = get_query( (fetched_article.title + ". " + fetched_article.text)[:400] )

        generated_query = filter_query_string(generated_query)

        if input_domain:
            generated_query = generated_query + " " + f"-site:{input_domain}"

        if fetched_article.publish_date:
            #parsed_date = datetime.datetime.fromisoformat(fetched_article.publish_date)
            parsed_date = fetched_article.publish_date

            after_date = (parsed_date - datetime.timedelta(weeks=4)).strftime("%Y-%m-%d")
            before_date = (parsed_date + datetime.timedelta(weeks=4)).strftime("%Y-%m-%d")


            generated_query = f"{generated_query} before:{before_date} after:{after_date}"

        print("Generated the query:", generated_query)

        routes = [a for a in search(f'{generated_query}', sleep_interval=1, num_results=6)]

        print("Unchecked routes:", routes)
    except Exception as e:
        print(e)
        return {
            "error": str(e)
        }

    checked_routes = []

    for route in routes:
        try:
            second_fetched_article = article(route)

            if not second_fetched_article.text:
                continue

            sample = {
                "title1": fetched_article.title,
                "text1": fetched_article.text,
                "title2": second_fetched_article.title,
                "text2": second_fetched_article.text,
            }

            parsed_date = None

            if second_fetched_article.publish_date:
                parsed_date = second_fetched_article.publish_date
                parsed_date = datetime.datetime.fromisoformat(str(parsed_date))
                parsed_date = parsed_date.strftime("%d %b %Y")

            domain_regex_run = re.search(domain_regex, route)
            route_domain = domain_regex_run.group(1)

            print("Parsed date and domain regex.")

            if route_domain == input_domain:
                print("Same domain for", route)
                continue

            new_route_obj = {
                "domain": route_domain,
                "link": route,
                "title": second_fetched_article.title,
                "publish_date": parsed_date,
                "top_image": second_fetched_article.top_image,
                "text": second_fetched_article.text[:500],
            }
        
            if check_match(sample) == 1:
                checked_routes.append(new_route_obj)
            else:
                print("Not matching:", route)
        except Exception as e:
            print(e)
            continue

    print("Got the checked routes", checked_routes)

    return checked_routes
    return ["link1", "link2"]

@app.route("/compute_diff", methods=["POST"])
def compute_diff():
    
    try:
        input_article1 = request.get_json()["article_link1"]
        input_article2 = request.get_json()["article_link2"]

        article1 = article(input_article1)
        article2 = article(input_article2)

        report = get_report(article1.text, article2.text)
        
        return {
            "output": report
        }

    except Exception as e:
        print(e)
        return {
            "error": str(e)
        }

    return {"output": "This is the diff!"}



#[a for a in search(f'asd', sleep_interval=2, num_results=4)]