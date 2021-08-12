from celery import shared_task
from subscribe.email import send_subscribed_email, send_review_email
from celery.utils.log import logger
from .scrapper import fetch_reviews_from_google_play, fetch_reviews_from_app_store
from .models import Subscriber, GooglePlay, AppStore, Subscription
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
    for subscriber in Subscriber.objects.all():
        id = subscriber.id
        print(id)
        send_reviews_based_on_subscription.delay(id)


@shared_task
def send_reviews_based_on_subscription(id):
    subscriber = Subscriber.objects.get(id=id)
    subscriptions = Subscription.objects.filter(subscriber=subscriber)
    for subscription in subscriptions:
        country_code = subscription.country.country_code
        country_name = subscription.country.country_name
        email = subscription.subscriber.email

        if subscription.app_store:
            id = subscription.app_store.id
            scrap_app_reviews_for_app_store.delay(id, country_code, country_name, email)

        elif subscription.google_play:
            id = subscription.google_play.id
            scrap_app_reviews_for_google_play.delay(id, country_code, country_name, email)

@shared_task
def scrap_app_reviews_for_app_store(id, country_code, country_name, email):
    app = AppStore.objects.get(pk=id)
    result = fetch_reviews_from_app_store(app.app_id, country_code)
    if result:
        send_review_email_task.delay(email=email,
                                     app_id=app.app_id,
                                     reviews=result,
                                     app_name=app.app_name,
                                     platform="App Store",
                                     app_icon=app.app_icon,
                                     country_name=country_name
                                     )

@shared_task
def scrap_app_reviews_for_google_play(id, country_code, country_name, email):
    app = GooglePlay.objects.get(pk=id)
    result = fetch_reviews_from_google_play(app.app_id, country_code)
    if result:
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