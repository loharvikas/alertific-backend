from datetime import datetime, time, timedelta
from google_play_scraper import Sort, reviews
from django.conf import settings
import requests
from requests.exceptions import HTTPError
from subscribe.models import  Subscription



def fetch_reviews_from_app_store(app_id, country_code, sub_id):
    """
    :param app_id:  Unique App Id.
    :param country_code: ISO Country Code.
    :return: Reviews from App Store
    """
    reviews = fetch_appstore_reviews(str(app_id), country_code, "1", sub_id)
    return reviews


def fetch_reviews_from_google_play(app_id, country_code, sub_id):
    """
    Use google_play_scraper library to fetch most recent reviews from Google Play Store.
    :param app_id: Unique App Id.
    :param country_code: ISO Country Code
    :return: List of reviews
    """
    subscription = Subscription.objects.get(pk=sub_id)
    results, continution_token = reviews(
        app_id,
        lang="en",
        country=country_code,
        sort=Sort.NEWEST,
        count=50,
    )
    all_reviews = []
    for result in results:
        result['version'] = result.pop('reviewCreatedVersion')
        date = result['at']
        date_time = datetime.strftime(date, '%Y-%m-%d')
        result['at'] = date_time
        print("USERNAME:", result["userName"])
        review_id = result["reviewId"]
        print(subscription.last_review_id, review_id)
        if review_id == subscription.last_review_id:
            print("BREAK")
            break
        all_reviews.append(result)
    if len(all_reviews) >= 30:
        last_review = all_reviews[0]
        print("USERNAMEXXX:", last_review["userName"])
        last_review_id = last_review["reviewId"]
        subscription.last_review_id = last_review_id
        subscription.save()

    return all_reviews


def fetch_appstore_reviews(app_id, country, page, sub_id):
    """
    Fetch reviews from Itunes RSS feeds.
    :param app_id:  Unique App Id.
    :param country:
    :param page: Numbers of page to be fetched max. 10
    :return: List of reviews
    """
    subscription = Subscription.objects.get(pk=sub_id)
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
        comment['reviewId'] = review['id']['label']
        comment['userName'] = review['author']['name']['label']
        comment['score'] = review['im:rating']['label']
        comment['title'] = review['title']['label']
        comment['content'] = review['content']['label']
        comment['version'] = review['im:version']['label']
        comment['at'] = review['updated']['label'].split('T')[0]
        review_id = comment["reviewId"]
        if review_id == subscription.last_review_id:
            print("BREAK")
            break
        reviews.append(comment)

    if len(reviews) >= 10:
        last_review = reviews[0]
        last_review_id = last_review["reviewId"]
        subscription.last_review_id = last_review_id
        subscription.save()

    return reviews