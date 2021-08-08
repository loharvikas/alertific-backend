from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings


def send_subscribed_email(email, app_id, platform, country, app_icon):
    print("SEND")
    """
    Sends confirmation mail to new users.
    :param email:
    :param app_id:
    :param platform:
    :param country:
    :return:
    """
    context = {
        'app_name': app_id,
        'platform': platform,
        'country': country,
        "app_icon": app_icon,
    }

    email_subject = "Your daily alert of new app reviews is live"
    html_content = render_to_string("subscribe/email_message.html", context)
    email_body = render_to_string('subscribe/email_message.txt', context)
    email = EmailMultiAlternatives(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [email, ]
    )
    email.attach_alternative(html_content, 'text/html')
    print("DONE")
    return email.send(fail_silently=False)



def send_feedback_email(email, message):
    context = {
        'email': email,
        'message': message,
    }
    email_subject = f"Feedback from {email}"
    email_body = render_to_string("subscribe/feedback_email.txt", context)
    html_content = render_to_string("subscribe/feedback_email.html", context)
    email = EmailMultiAlternatives(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [settings.DEFAULT_FROM_EMAIL, ]
    )
    email.attach_alternative(html_content, "text/html")
    email.send(fail_silently=False)
    print("SEND")


def send_review_email(email, app_name, app_id, reviews, platform, app_icon, country):
    """

    :param email: User's email.
    :param app_name: App name of subscribed app.
    :param app_id: Unique App Id
    :param reviews: List of reviews.
    :param platform: App store of Platform
    :param app_icon:
    :param country:
    :return:
    """
    for review in reviews:
        active = []
        for i in range(int(review['score'])): # Creates List for looping in django template and adding star image
            # accordingly
            active.append('I')
        remaining = []
        value = 5 - int(review['score'])
        for i in range(value):
            remaining.append('I')
        review['remaining'] = remaining
        review['score'] = active


    context = {
        'app_name': app_name,
        'app_id': app_id,
        'reviews': reviews,
        'platform': platform,
        'app_icon': app_icon,
        'total_reviews': "50+" if len(reviews) >= 50 else len(reviews),
        'country': country
    }
    email_subject = "Your app has new reviews"
    html_content = render_to_string("subscribe/email_review.html", context)
    email_body = render_to_string('subscribe/email_review.txt', context)
    email = EmailMultiAlternatives(
        email_subject,
        email_body,
        settings.DEFAULT_FROM_EMAIL,
        [email, ]
    )
    email.attach_alternative(html_content, 'text/html')
    return email.send(fail_silently=False)
