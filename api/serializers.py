from rest_framework import serializers
from subscribe.models import Subscriber, AppStore, GooglePlay, Feedback, Country
from subscribe.tasks import send_subscribe_email_task, send_feedback_email_task
from rest_framework import status
from rest_framework.response import Response
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
    app_store = AppStoreSerializer(required=False, many=True)
    google_play = GooglePlaySerializer(required=False, many=True)

    class Meta:
        model = Country
        fields = '__all__'
        extra_kwargs = {
            'country_code': {'validators': []},
        }


class SubscriberSerializer(serializers.ModelSerializer):
    app_store = AppStoreSerializer(required=False, many=True)
    google_play = GooglePlaySerializer(required=False, many=True)
    country = CountrySerializer(required=False, many=True)

    class Meta:
        model = Subscriber
        fields = '__all__'
        extra_kwargs = {
            'email': {'validators': []},
        }
        depth = 1

    def create(self, validated_data):
        """
        :param validated_data:
        :return: Subscriber Instance
        """
        print("VALIDS:", validated_data)
        country_created = False  # To check if existing user adds new country
        validated_data, app_created, platform = self.create_apps(
            validated_data)
        validated_data, send_mail = self.create_country(
            validated_data, app_created)
        subscriber, sub_created, = Subscriber.objects.get_or_create(
            email=validated_data['email'])
        if 'app_store' in validated_data:
            app_store_obj = validated_data['app_store']
            if app_store_obj not in subscriber.app_store.all():
                send_mail = True
                subscriber.app_store.add(app_store_obj)
                app_name = app_store_obj.app_name
        if 'google_play' in validated_data:
            google_play_obj = validated_data['google_play']
            if google_play_obj not in subscriber.google_play.all():
                send_mail = True
                subscriber.google_play.add(google_play_obj)
                app_name = google_play_obj.app_name
        country_obj = validated_data["country"]
        print(country_obj)
        print("COUNTRY_CREATED:", country_created)
        print("APP:", app_created)
        subscriber.country.add(country_obj)
        if send_mail:  # checks if new object was created and sends email confirmation
            print("SENDING")
            send_subscribe_email_task.delay(
                validated_data['email'], app_name, platform, country_obj.country_name)
            subscriber.save()
            return subscriber
        raise serializers.ValidationError()

    def create_country(self, validated_data, app_created):
        """
        :param validated_data:
        :return:
        """
        country = validated_data.get('country')
        google_play = validated_data.get('google_play')
        app_store = validated_data.get('app_store')
        send_mail = False
        if country:
            country = country[0]
            country_code = country.pop("country_code")
            country_name = convert_iso_to_country(country_code)
            print("COUNTRY_NAME:", country_name)
            country, created = Country.objects.get_or_create(
                country_code=country_code)
            if app_store:
                app_store_obj = validated_data['app_store']
                print("APPSTORE:", app_store_obj)
                if app_store_obj not in country.app_store.all():
                    send_mail = True
                    country.app_store.add(app_store_obj)
            if google_play:
                google_play_obj = validated_data['google_play']
                print("GOOGLE:", google_play_obj)
                if google_play_obj not in country.google_play.all():
                    send_mail = True
                    country.google_play.add(google_play_obj)
            country.country_name = country_name
            country.save()
        validated_data["country"] = country
        return validated_data, send_mail

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
            google_play = google_play[0]
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
            app_store = app_store[0]
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

        return validated_data, created, platform


class FeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = Feedback
        fields = '__all__'

    def create(self, validated_data):
        feedback = Feedback.objects.create(**validated_data)
        send_feedback_email_task.delay(feedback.email, feedback.message)
        return feedback
