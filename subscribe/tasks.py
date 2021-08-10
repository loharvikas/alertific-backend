from celery import shared_task
from subscribe.email import send_subscribed_email, send_review_email
from celery.utils.log import logger
from .scrapper import fetch_reviews_from_google_play, fetch_reviews_from_app_store
from .models import Subscriber, GooglePlay, AppStore
from .email import send_feedback_email


@shared_task
def send_subscribe_email_task(email, app_id, platform, country, app_icon):
    logger.info("Email Sent")
    return send_subscribed_email(email, app_id, platform, country, app_icon)


@shared_task
def send_feedback_email_task(email, message):
    logger.info("Email sent")
    return send_feedback_email(email, message)


@shared_task
def send_app_reviews():
    scrap_google_play.delay()
    scrap_app_store.delay()


@shared_task
def scrap_google_play():
    apps = GooglePlay.objects.all()
    for app in apps:
        scrap_app_reviews_for_google_play.delay(app.pk)


@shared_task
def scrap_app_store():
    apps = AppStore.objects.all()
    for app in apps:
        print("APP:", app)
        scrap_app_reviews_for_app_store.delay(app.pk)


@shared_task
def scrap_app_reviews_for_app_store(id):
    """
       Scrap app reviews and send emails to subscribed users
    :param id:
    :return: None
    """
    app = AppStore.objects.get(pk=id)
    subscriber_list = app.subscriber.all()
    for subscriber in subscriber_list:
        print("SUBSCRIBER: SENDING EMAILS APP STORE", subscriber.email)
        countries = subscriber.country.all()  # List of countries
        for country in countries:
            if app in country.app_store.all():
                print("YES")
                scrap_app_reviews_for_app_store_specific_country.delay(id=id,
                                                                       country_code=country.country_code,
                                                                       country_name=country.country_name,
                                                                       email=subscriber.email)
        # for i in range(len(country)):
        #     scrap_app_reviews_for_app_store_specific_country.delay(id=id,
        #                                                            country_code=country[i].code,
        #                                                            country_name=country[i].name,
        #                                                            email=subscriber.email)


@shared_task
def scrap_app_reviews_for_app_store_specific_country(id, country_code, country_name, email):
    app = AppStore.objects.get(pk=id)
    result = fetch_reviews_from_app_store(app.app_id, country_code)
    send_review_email_task.delay(email=email,
                                 app_id=app.app_id,
                                 reviews=result,
                                 app_name=app.app_name,
                                 platform="App Store",
                                 app_icon=app.app_icon,
                                 country_name=country_name
                                 )


@shared_task
def scrap_app_reviews_for_google_play(id):
    """
    Scrap app reviews and send emails to subscribed users
    :param id:
    :return: None
    """
    app = GooglePlay.objects.get(pk=id)
    subscriber_list = app.subscriber.all()
    for subscriber in subscriber_list:
        print("SUBSCRIBER: SENDING EMAILS", subscriber.email)
        countries = subscriber.country.all()
        for country in countries:
            if app in country.google_play.all():
                print("YES")
                scrap_app_reviews_for_google_play_specific_country.delay(id=id,
                                                                         country_code=country.country_code,
                                                                         country_name=country.country_name,
                                                                         email=subscriber.email)


@shared_task
def scrap_app_reviews_for_google_play_specific_country(id, country_code, country_name, email):
    app = GooglePlay.objects.get(pk=id)
    result = fetch_reviews_from_google_play(app.app_id, country_code)
    send_review_email_task.delay(email=email,
                                 app_id=app.app_id,
                                 reviews=result,
                                 app_name=app.app_name,
                                 platform="Google Play",
                                 app_icon=app.app_icon,
                                 country_name=country_name
                                 )


@shared_task
def send_review_email_task(email, app_name, app_id, reviews, platform, app_icon, country_name):
    logger.info("SENDING REVIEW EMAIL")
    return send_review_email(email, app_name, app_id, reviews, platform, app_icon, country_name)
