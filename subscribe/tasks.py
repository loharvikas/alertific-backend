
from celery import shared_task
from subscribe.email import send_subscribed_email, send_review_email
from celery.utils.log import logger
from .scrapper import fetch_reviews_from_google_play, fetch_reviews_from_app_store
from .models import Subscriber, GooglePlay, AppStore, Subscription
from .email import send_feedback_email


@shared_task
def send_subscribe_email_task(email, app_name, platform, country, app_icon, sub_id):
    logger.info("Email Sent")
    return send_subscribed_email(email, app_name, platform, country, app_icon, sub_id)


@shared_task
def fetch_initial_review(app_id, platform, sub_id, country_code):
    subscription = Subscription.objects.get(pk=sub_id)
    if platform == "Google Play":
        reviews = fetch_reviews_from_google_play(app_id, country_code, sub_id)
        last_review = reviews[0]
        last_review_id = last_review["reviewId"]
        subscription.last_review_id = last_review_id
        print("Last_review:::", last_review_id)
        subscription.save()
    else:
        reviews = fetch_reviews_from_app_store(app_id, country_code, sub_id)
        last_review = reviews[0]
        last_review_id = last_review["reviewId"]
        subscription.last_review_id = last_review_id
        subscription.save()


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
        sub_id = subscription.pk
        if subscription.app_store:
            id = subscription.app_store.id
            scrap_app_reviews_for_app_store.delay(id, country_code, country_name, email, sub_id)

        elif subscription.google_play:
            id = subscription.google_play.id
            scrap_app_reviews_for_google_play.delay(id, country_code, country_name, email, sub_id)


@shared_task
def scrap_app_reviews_for_app_store(id, country_code, country_name, email, sub_id):
    app = AppStore.objects.get(pk=id)
    result = fetch_reviews_from_app_store(app.app_id, country_code, sub_id)
    if len(result) > 1:
        send_review_email_task.delay(email=email,
                                     app_id=app.app_id,
                                     reviews=result,
                                     app_name=app.app_name,
                                     platform="App Store",
                                     app_icon=app.app_icon,
                                     country_name=country_name,
                                     sub_id=sub_id
                                     )


@shared_task
def scrap_app_reviews_for_google_play(id, country_code, country_name, email, sub_id):
    app = GooglePlay.objects.get(pk=id)
    result = fetch_reviews_from_google_play(app.app_id, country_code, sub_id)
    if len(result) >= 30:
        send_review_email_task.delay(email=email,
                                     app_id=app.app_id,
                                     reviews=result,
                                     app_name=app.app_name,
                                     platform="Google Play",
                                     app_icon=app.app_icon,
                                     country_name=country_name,
                                     sub_id=sub_id
                                     )


@shared_task
def send_review_email_task(email, app_name, app_id, reviews, platform, app_icon, country_name, sub_id):
    logger.info("SENDING REVIEW EMAIL")
    return send_review_email(email, app_name, app_id, reviews, platform, app_icon, country_name, sub_id)