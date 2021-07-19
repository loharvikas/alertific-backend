from django.urls import path
from .views import (GooglePlayFormView,
                    GooglePlayAppListView,
                    GoogleSubscribeFormView,
                    HomePageView,
                    AppStoreFormView,
                    AppStoreAppListView,
                    AppStoreSubscribeForm)

app_name = "subscribe"

urlpatterns = [
    path("", HomePageView.as_view(), name="home"),
    path("google/", GooglePlayFormView.as_view(), name="google"),
    path("google/<str:app_name>/", GooglePlayAppListView.as_view(), name="google-app-list"),
    path("google_subscribe/<str:app_id>/", GoogleSubscribeFormView.as_view(), name='google-subscribe'),
    path("apple/", AppStoreFormView.as_view(), name="app-store"),
    path("apple/<str:app_name>/",AppStoreAppListView.as_view(), name="app-store-app-list" ),
    path("app_store_subscribe/<str:app_id>/", AppStoreSubscribeForm.as_view(), name="apple-subscribe")
]
