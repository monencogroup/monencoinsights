from django.conf.urls import url
from API.views import (
    RegisterView,
    LoginView,
    RefreshTokenView,
    LogoutView,
    ConfigsView,
    CategoryListToggleView,
    ArticleSearchView,
    ArticleBookmarkToggleView,
    ArticleBookmarkListView,
    ArticleView,
    PurchaseCallbackView,
    ArticlePurchaseView,
    PurchaseListView,
    BazarTokenView,
    PaymentCheck,
)

app_name = 'API'
urlpatterns = [
    url(r'^authentication/register/', RegisterView.as_view()),
    url(r'^authentication/login/', LoginView.as_view()),
    url(r'^authentication/token/refresh/', RefreshTokenView.as_view()),
    url(r'^authentication/logout', LogoutView.as_view()),

    url(r'^configs/', ConfigsView.as_view()),

    url(r'^category/list/toggle/', CategoryListToggleView.as_view()),

    url(r'^article/search/', ArticleSearchView.as_view()),
    url(r'^article/bookmark/toggle/', ArticleBookmarkToggleView.as_view()),
    url(r'^article/bookmark/list/', ArticleBookmarkListView.as_view()),
    url(r'^article/purchase/callback/', PurchaseCallbackView.as_view()),
    url(r'^article/purchase/list/', PurchaseListView.as_view()),
    url(r'^article/purchase/', ArticlePurchaseView.as_view()),
    url(r'^article/payment/check/', PaymentCheck.as_view()),
    url(r'^article/', ArticleView.as_view()),
    url(r'^bazar/token/', BazarTokenView.as_view()),
]
