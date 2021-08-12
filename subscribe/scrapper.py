from datetime import datetime, time, timedelta
from google_play_scraper import Sort, reviews
from django.conf import settings
import requests
from requests.exceptions import HTTPError


def is_yesterday(timestamp):
    """
    :param timestamp:
    :return: Checks if timestamp of reviews was posted between specific time
    """
    today = datetime.combine(datetime.today(), time.min) + timedelta(hours=9)
    yesterday = today - timedelta(days=1)
    return True
    # return yesterday <= timestamp < today


def fetch_reviews_from_app_store(app_id, country_code):
    """
    :param app_id:  Unique App Id.
    :param country_code: ISO Country Code.
    :return: Reviews from App Store
    """
    reviews = fetch_appstore_reviews(str(app_id), country_code, "1")
    return reviews


def fetch_reviews_from_google_play(app_id, country_code):
    """
    Use google_play_scraper library to fetch most recent reviews from Google Play Store.
    :param app_id: Unique App Id.
    :param country_code: ISO Country Code
    :return: List of reviews
    """
    print("GOOGLE_PLAY:", app_id)
    print("COUNTRY:", country_code)
    results, continution_token = reviews(
        app_id,
        lang="en",
        country=country_code,
        sort=Sort.NEWEST,
    )
    result_by_date = []
    for result in results:
        result['version'] = result.pop('reviewCreatedVersion')
        date_time = result['at']
        if is_yesterday(date_time):
            date_time = datetime.strftime(date_time, '%Y-%m-%d')
            result['at'] = date_time
            result_by_date.append(result)
    return result_by_date


def fetch_appstore_reviews(app_id, country, page):
    """
    Fetch reviews from Itunes RSS feeds.
    :param app_id:  Unique App Id.
    :param country:
    :param page: Numbers of page to be fetched max. 10
    :return: List of reviews
    """
    url = 'https://itunes.apple.com/rss/customerreviews/page=' + page + '/id=' + app_id + '/sortby=mostrecent/json?cc=' + country
    print(url)
    try:
        response = requests.get(url)
        response.raise_for_status()
    except HTTPError as http_err:
        print(f'HTTP error occurred: {http_err}')
    except Exception as err:
        print(f'Other error occurred: {err}')
    else:
        print("Success")

    content = response.json()
    entry = content['feed']['entry']

    reviews = list()
    for review in entry:
        comment = dict()
        comment['id'] = review['id']['label']
        comment['userName'] = review['author']['name']['label']
        comment['score'] = review['im:rating']['label']
        comment['title'] = review['title']['label']
        comment['content'] = review['content']['label']
        comment['version'] = review['im:version']['label']
        comment['at'] = review['updated']['label'].split('T')[0]
        date = comment['at']
        date_time = datetime.strptime(date, '%Y-%m-%d')
        if is_yesterday(date_time):
            reviews.append(comment)

    return reviews
