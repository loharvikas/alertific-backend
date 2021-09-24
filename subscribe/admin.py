from django.contrib import admin
from import_export.admin import ImportExportModelAdmin
from import_export.fields import Field
from import_export import resources
from .models import Subscriber, GooglePlay, AppStore, Country, Subscription

admin.site.register(Subscriber)
admin.site.register(GooglePlay)
admin.site.register(AppStore)
admin.site.register(Country)


class SubscriptionResource(resources.ModelResource):
    subscriber = Field(attribute="Subscriber", column_name="Subscriber")
    google_play = Field(attribute="Google Play", column_name="Google Play")
    app_store = Field(attribute="App Store", column_name="App Store")
    country = Field(attribute="Country", column_name="Country")

    class Meta:
        model = Subscription
        fields = ("subscriber", "google_play", "app_store", "country", "created")

    def dehydrate_subscriber(self, subs):
        return subs.subscriber.email

    def dehydrate_google_play(self, subs):
        if subs.google_play:
            return subs.google_play.app_name
        return "None"

    def dehydrate_app_store(self, subs):
        if subs.app_store:
            return subs.app_store.app_name
        return "None"

    def dehydrate_country(self, subs):
        return subs.country.country_name


class SubscriptionAdmin(ImportExportModelAdmin):
    resource_class = SubscriptionResource



admin.site.register(Subscription, SubscriptionAdmin)