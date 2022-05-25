from rest_framework import serializers
from subscribe.models import Subscriber, AppStore, GooglePlay, Feedback, Country, Subscription
from subscribe.tasks import send_subscribe_email_task, send_feedback_email_task, fetch_initial_review
import pycountry


def convert_iso_to_country(iso_code):
    country = pycountry.countries.get(alpha_2=iso_code)
    return country.name


class AppStoreSerializer(serializers.ModelSerializer):
    class Meta:
        model = AppStore
        fields = ('app_id', 'app_name', 'developer_id', 'app_icon')


class GooglePlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = GooglePlay
        fields = ('app_id', 'app_name', 'developer_id', 'app_icon')


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'
        extra_kwargs = {
            'country_code': {'validators': []},
        }


class SubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subscriber
        fields = ('email', 'created')
        extra_kwargs = {
            'email': {'validators': []},
        }


class SubscriptionSerializer(serializers.ModelSerializer):
    app_store = AppStoreSerializer(required=False)
    google_play = GooglePlaySerializer(required=False)
    country = CountrySerializer(required=False)
    subscriber = SubscriberSerializer(required=False)

    class Meta:
        model = Subscription
        fields = '__all__'
        depth = 1

    def create(self, validated_data):
        country_created = False  # To check if existing user adds new country
        validated_data, platform = self.create_apps(validated_data)
        validated_data = self.create_country(validated_data)
        validated_data = self.create_subscriber(validated_data)
        country = validated_data["country"]
        subscriber = validated_data["subscriber"]
        subscription = None
        if "google_play" in validated_data:
            google_play = validated_data["google_play"]
            app_name = google_play.app_name
            app_icon = google_play.app_icon
            app_id = google_play.app_id
            if not Subscription.objects.filter(google_play=google_play, subscriber=subscriber,
                                               country=country).exists():
                subscription = Subscription.objects.create(
                    google_play=google_play,
                    subscriber=subscriber,
                    country=country
                )
        if "app_store" in validated_data:
            app_store = validated_data["app_store"]
            app_name = app_store.app_name
            app_icon = app_store.app_icon
            app_id = app_store.app_id
            if not Subscription.objects.filter(app_store=app_store, subscriber=subscriber, country=country).exists():
                subscription = Subscription.objects.create(
                    app_store=app_store,
                    subscriber=subscriber,
                    country=country
                )
        if subscription:
            send_subscribe_email_task.delay(subscriber.email,
                                            app_name,
                                            platform,
                                            country.country_name,
                                            app_icon,
                                            subscription.pk)
            fetch_initial_review.delay(
                app_id, platform, subscription.pk, country.country_code)
            return subscription
        raise serializers.ValidationError()

    def create_country(self, validated_data):
        """
        :param validated_data:
        :return:
        """
        country = validated_data.get('country')
        if country:
            country_code = country.pop("country_code")
            country_name = convert_iso_to_country(country_code)
            country, created = Country.objects.get_or_create(
                country_code=country_code)
            country.country_name = country_name
            country.save()
        validated_data["country"] = country
        return validated_data

    def create_subscriber(self, validated_data):
        subscriber = validated_data.get("subscriber")
        if subscriber:
            email = subscriber.pop("email")
            subscriber_obj, sub_created, = Subscriber.objects.get_or_create(
                email=email)
        validated_data["subscriber"] = subscriber_obj
        return validated_data

    def create_apps(self, validated_data):
        """
        Creates GooglePlay and Appstore Objects.
        :param validated_data:
        :return:
        """
        google_play = validated_data.get('google_play')
        app_store = validated_data.get('app_store')
        platform = None
        if google_play:
            app_id = google_play.pop('app_id')
            app_name = google_play.pop('app_name')
            developer_id = google_play.pop('developer_id')
            app_icon = google_play.pop('app_icon')
            google_play_obj, created = GooglePlay.objects.get_or_create(
                app_id=app_id,
                app_name=app_name,
                developer_id=developer_id,
                app_icon=app_icon
            )
            validated_data['google_play'] = google_play_obj
            platform = 'Google Play'

        if app_store:
            app_id = app_store.pop('app_id')
            app_name = app_store.pop('app_name')
            developer_id = app_store.pop('developer_id')
            app_icon = app_store.pop('app_icon')
            app_store_obj, created = AppStore.objects.get_or_create(
                app_id=app_id,
                app_name=app_name,
                developer_id=developer_id,
                app_icon=app_icon
            )
            validated_data['app_store'] = app_store_obj
            platform = 'the App Store'

        return validated_data, platform


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

    def create(self, validated_data):
        feedback = Feedback.objects.create(**validated_data)
        send_feedback_email_task.delay(feedback.email, feedback.message)
        return feedback
