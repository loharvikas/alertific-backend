from rest_framework.viewsets import generics
from subscribe.models import Subscriber, Feedback, Subscription
from .serializers import SubscriberSerializer, FeedbackSerializer, SubscriptionSerializer
from rest_framework.permissions import AllowAny
from django.views.generic import View
import play_scraper
from itunes_app_scraper.scraper import AppStoreScraper
from django.conf import settings
from django.http import JsonResponse, HttpResponse, HttpResponseNotFound
import os


class SubscriberAPIListView(generics.ListCreateAPIView):
    """
        SerializerView for creating subscriber.
        API endpoint: api/subscribe/
    """
    queryset = Subscriber.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SubscriberSerializer


class SubscriberDetailView(generics.RetrieveAPIView):
    queryset = Subscriber.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SubscriberSerializer


class SubscriptionListView(generics.ListCreateAPIView):
    queryset = Subscription.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = SubscriptionSerializer


class FeedbackSerializerView(generics.ListCreateAPIView):
    """
        SerializerView for creating feedback
        API endpoint: api/feedback/
    """
    queryset = Feedback.objects.all()
    serializer_class = FeedbackSerializer
    permission_classes = (AllowAny,)


class GooglePlayAppListView(View):
    """
        Uses play_scraper library to search Google Play store
        API Endpoint: api/google/app_name/
        :return List of apps in JSON format.
    """

    def get(self, request, app_name, country_code, *args, **kwargs):
        """
        :param request:
        :param app_name: Use to search Google Play Store
        :param args:
        :param kwargs:
        :return: List of apps in JSON format.
        """
        print("APP_NAME:", app_name)
        print(request)
        country_code = str(country_code).lower()
        data = play_scraper.search(app_name, page=1, gl=country_code)
        return JsonResponse(data, safe=False)


class AppStoreAppListView(View):
    """
        Uses itunes_app_scraper library to search App  store
        API Endpoint: api/apple/app_name/
    """

    def get(self, request, app_name, country_code, *args, **kwargs):
        """
        :param request:
        :param app_name: Use to search App store
        :param args:
        :param kwargs:
        :return: List of apps in JSON format.
        """
        scraper = AppStoreScraper()
        results = scraper.get_app_ids_for_query(app_name, country=country_code)
        if len(results):
            results = results[:8]
        data = []
        for i in results:
            detail = scraper.get_app_details(app_id=i, country=country_code)
            detail['title'] = detail.pop('trackName')
            detail['developer'] = detail.pop('artistName')
            detail['developer_id'] = detail.pop('artistId')
            detail['app_id'] = detail.pop('trackId')
            detail['icon'] = detail.pop('artworkUrl512')
            data.append(detail)
        return JsonResponse(data, safe=False)
