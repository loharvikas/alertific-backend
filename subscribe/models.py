
from django.db import models


class GooglePlay(models.Model):
    app_id = models.CharField(max_length=50)
    app_name = models.CharField(max_length=50, null=True, blank=True)
    developer_id = models.CharField(max_length=50, null=True, blank=True)
    app_icon = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'{self.app_id}'


class AppStore(models.Model):
    app_id = models.CharField(max_length=50)
    app_name = models.CharField(max_length=50, null=True, blank=True)
    developer_id = models.CharField(max_length=50, null=True, blank=True)
    app_icon = models.URLField(blank=True, null=True)

    def __str__(self):
        return f'{self.app_id} - {self.app_name}'


class Subscriber(models.Model):
    email = models.EmailField(unique=False)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.email


class Subscription(models.Model):
    google_play = models.ForeignKey(GooglePlay, on_delete=models.SET_NULL, null=True, blank=True)
    app_store = models.ForeignKey(AppStore, on_delete=models.SET_NULL, null=True, blank=True)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True,  blank=True)
    subscriber = models.ForeignKey(Subscriber, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True, null=True, blank=True)


class Country(models.Model):
    country_code = models.CharField(max_length=2, unique=True)
    country_name = models.CharField(max_length=50, null=True, blank=True)


    def __str__(self):
        return self.country_code


class Feedback(models.Model):
    email = models.EmailField(unique=False)
    message = models.TextField()

    def __str__(self):
        return self.email