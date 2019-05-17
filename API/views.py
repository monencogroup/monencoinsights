import requests
from django.contrib.auth.models import User
from django.db.models import Q
from django.http import HttpResponse
from oauth2_provider.ext.rest_framework import TokenHasReadWriteScope
from rest_framework import status
from rest_framework.generics import ListAPIView
from rest_framework.permissions import (
    AllowAny,
    IsAuthenticated,
)
from rest_framework.response import Response
from rest_framework.views import APIView
from suds import client as C1

from API.models import (Client, Category, Article, Configs, PurchaseBankID, Tag, BazarToken)
from API.serializers import (UserRegisterSerializer,
                             LoginSerializer,
                             RefreshTokenSerializer,
                             LogoutSerializer,
                             ConfigsSerializer,
                             ToggleSetSerializer,
                             ArticleCompactSerializer,
                             ArticleSerializer,
                             ToggleSerializer,
                             PurchaseArticleSerializer,
                             PaymentCheckSerializer,
                             )

MMERCHANT_ID = '2f61cc7c-a3fe-11e6-8bd7-005056a205be'
ZARINPAL_WEBSERVICE = 'https://www.zarinpal.com/pg/services/WebGate/wsdl'


# Fully OK
class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            dataDictionary = serializer.validated_data
            username = dataDictionary['username']
            password = dataDictionary['password']
            email = dataDictionary['email']
            data = dict()
            if User.objects.filter(username=username).exists():
                data['message'] = "client exists"
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create(username=username, email=email, is_active=True)
            user.set_password(password)
            user.save()
            tokenData = dict()
            tokenData['client_id'] = dataDictionary['client_id']
            tokenData['client_secret'] = dataDictionary['client_secret']
            tokenData['username'] = dataDictionary['username']
            tokenData['password'] = dataDictionary['password']
            tokenData['grant_type'] = 'password'
            absolute_url = request.build_absolute_uri('/')
            url = absolute_url + "o/auth/token/"
            result = requests.post(url, data=tokenData)
            if result.status_code != 200:
                user.delete()
                data['message'] = "unexpected error"
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            Client.objects.create(user=user)
            return Response(result.json(), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Fully OK
class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            dataDictionary = serializer.validated_data
            grant_type = dataDictionary['grant_type']
            if str(grant_type) != "password":
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            absolute_url = request.build_absolute_uri('/')
            url = absolute_url + "o/auth/token/"
            result = requests.post(url, data=serializer.data)
            if result.status_code != 200:
                data = dict()
                data['message'] = "invalid username or password"
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(result.json(), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


# Fully OK
class RefreshTokenView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RefreshTokenSerializer(data=request.data)
        if serializer.is_valid():
            dataDictionary = serializer.validated_data
            grant_type = dataDictionary['grant_type']
            if str(grant_type) != "refresh_token":
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            absolute_url = request.build_absolute_uri('/')
            url = absolute_url + "o/auth/token/"
            result = requests.post(url, data=serializer.data)
            if result.status_code != 200:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(result.json(), status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


# Fully OK
class LogoutView(APIView):
    permission_classes = [IsAuthenticated, TokenHasReadWriteScope]

    def post(self, request):
        try:
            user = request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            absolute_url = request.build_absolute_uri('/')
            url = absolute_url + "o/auth/revoke_token/"
            result = requests.post(url, data=serializer.data)
            if result.status_code != 200:
                return Response(status=status.HTTP_401_UNAUTHORIZED)
            return Response(status=result.status_code)
        else:
            return Response(status=status.HTTP_401_UNAUTHORIZED)


# Fully OK
class ConfigsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = self.request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        configs = Configs.objects.all().first()
        serializer = ConfigsSerializer(configs, context={'request': request, 'isPersian': isPersian})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


# Fully OK
class CategoryListToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = ToggleSetSerializer(data=request.data)
        if serializer.is_valid():
            toggleSet = serializer.validated_data['toggleSet']
            for toggleItem in toggleSet:
                if Category.objects.filter(id=toggleItem['id']).exists() is False:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            for toggleItem in toggleSet:
                category = Category.objects.get(id=toggleItem['id'])
                newState = toggleItem['newState']
                if newState:
                    if (category in client.favoriteCategories.all()) is False:
                        client.favoriteCategories.add(category)
                else:
                    if category in client.favoriteCategories.all():
                        client.favoriteCategories.remove(category)
            client.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Fully OK
class ArticleSearchView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleCompactSerializer

    def get_serializer_context(self):
        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        return {'request': self.request, 'isPersian': isPersian}

    def get_queryset(self):
        try:
            user = self.request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            query_text = self.request.query_params.get('query')
            if query_text is None:
                query_text = ""
        except:
            query_text = ""
        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        if query_text == "":
            return []
        tags = Tag.objects.filter(Q(name__icontains=query_text) | Q(persianName__icontains=query_text))
        articles = Article.objects.filter(
            Q(title__icontains=query_text) | Q(leadText__icontains=query_text) | Q(tags__in=tags),
            category__in=client.favoriteCategories.all(),
            isPersian=isPersian,
            published=True).distinct().order_by("-creationDate")
        return articles[:10]


# Fully OK
class ArticleBookmarkToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = ToggleSerializer(data=request.data)
        if serializer.is_valid():
            articleId = serializer.validated_data['id']
            newState = serializer.validated_data['newState']
            if Article.objects.filter(id=articleId).exists() is False:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            article = Article.objects.get(id=articleId)
            if newState:
                if (article in client.bookmarkedArticles.all()) is False:
                    client.bookmarkedArticles.add(article)
            else:
                if article in client.bookmarkedArticles.all():
                    client.bookmarkedArticles.remove(article)
            client.save()
            return Response(status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


# Fully OK
class ArticleBookmarkListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleCompactSerializer

    def get_serializer_context(self):
        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        return {'request': self.request, 'isPersian': isPersian}

    def get_queryset(self):
        try:
            user = self.request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            query_text = self.request.query_params.get('query')
            if query_text is None:
                query_text = ""
        except:
            query_text = ""
        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        articles = client.bookmarkedArticles.filter(isPersian=isPersian, published=True).order_by("-creationDate")
        return articles


# Fully OK
class ArticleView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            articleId = self.request.query_params.get('id')
            article = Article.objects.get(id=articleId, published=True)
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = ArticleSerializer(article, context={'request': request, 'isPersian': article.isPersian})
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class ArticlePurchaseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = PurchaseArticleSerializer(data=request.data)
        if serializer.is_valid():
            articleId = serializer.validated_data["articleID"]
            platform = str(serializer.validated_data["platform"])
            if Article.objects.filter(id=articleId).exists() is False:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if platform != "Android" and platform != "iOS":
                return Response(status=status.HTTP_400_BAD_REQUEST)
            article = Article.objects.get(id=articleId)
            if article in client.purchasedArticles.all():
                return Response(status=status.HTTP_400_BAD_REQUEST)
            if article.price == 0:
                return Response(status=status.HTTP_400_BAD_REQUEST)

            if PurchaseBankID.objects.filter(article=article, client=client).exists():
                PurchaseBankID.objects.filter(article=article, client=client).delete()
            price = article.price
            if article.isPersian:
                description = "خرید مقاله: " + article.title
            else:
                description = "Purchasing Article: " + article.title
            zarin_client = C1.Client(ZARINPAL_WEBSERVICE)
            absolute_url = request.build_absolute_uri('/')
            call_back_url = absolute_url + 'api/v1/article/purchase/callback/'
            result = zarin_client.service.PaymentRequest(
                MerchantID=MMERCHANT_ID,
                Amount=price,
                Description=description,
                CallbackURL=call_back_url,
            )
            if result.Status == 100:
                authorizationID = str(result.Authority)
                PurchaseBankID.objects.create(article=article, client=client, authorityID=authorizationID,
                                              platform=platform)
                zarin_url = 'https://www.zarinpal.com/pg/StartPay/' + authorizationID
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            result['url'] = zarin_url
            return Response(result, status=status.HTTP_200_OK)

        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)


class PurchaseCallbackView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        zarin_status = request.query_params.get('Status', None)
        authorizationID = str(request.query_params.get('Authority', None))
        if PurchaseBankID.objects.filter(authorityID=authorizationID).exists() is False:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        bankID = PurchaseBankID.objects.get(authorityID=authorizationID)
        platform = bankID.platform
        article = bankID.article
        client = bankID.client
        if zarin_status == 'OK':
            zarin_client = C1.Client(ZARINPAL_WEBSERVICE)
            result = zarin_client.service.PaymentVerification(
                MerchantID=MMERCHANT_ID,
                Authority=authorizationID,
                Amount=bankID.article.price,
            )
            if result.Status == 100:
                client.purchasedArticles.add(article)
                client.save()
                bankID.delete()
                if platform == 'iOS':
                    app_url = 'monencoinsights://?status=1&article=' + str(article.id)
                else:
                    app_url = "intent://www.monencoinsights.com/#Intent;scheme=monenco;package=com.monenco.insights;i.status=1;i.article={};end".format(
                        str(article.id))
                response = HttpResponse("", status=302)
                response['Location'] = app_url
                return response
        if platform == 'iOS':
            app_url = 'monencoinsights://?status=0&article=' + str(article.id)
        else:
            app_url = "intent://www.monencoinsights.com/#Intent;scheme=monenco;package=com.monenco.insights;i.status=0;i.article={};end".format(
                str(article.id))
        response = HttpResponse("", status=302)
        response['Location'] = app_url
        return response


class PurchaseListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ArticleCompactSerializer

    def get_serializer_context(self):
        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        return {'request': self.request, 'isPersian': isPersian}

    def get_queryset(self):
        try:
            user = self.request.user
            client = user.client
        except:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        try:
            query_text = self.request.query_params.get('query')
            if query_text is None:
                query_text = ""
        except:
            query_text = ""
        try:
            isPersian = str(self.request.query_params.get('lang')) == "fa"
        except:
            isPersian = False
        articles = client.purchasedArticles.filter(isPersian=isPersian, published=True).order_by("-creationDate")
        return articles


class BazarTokenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        configs = Configs.objects.all().first()
        code = request.query_params.get('code', None)
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        configs.cafeBazarCode = code
        configs.save()
        return Response(status=status.HTTP_200_OK)


class PaymentCheck(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        client = request.user.client
        if client is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        serializer = PaymentCheckSerializer(data=request.data)
        if serializer.is_valid():
            token = self.getToken()
            if token is None:
                return Response(status=status.HTTP_412_PRECONDITION_FAILED)

            dataDictionary = serializer.validated_data
            paymentId = dataDictionary['paymentId']
            paymentToken = dataDictionary['paymentToken']

            if Article.objects.filter(cafeBazarPaymentId=paymentId).exists() is False:
                return Response(status=status.HTTP_400_BAD_REQUEST)
            article = Article.objects.get(cafeBazarPaymentId=paymentId)

            url = "https://pardakht.cafebazaar.ir/devapi/v2/api/validate/com.monenco.insights/inapp/" + paymentId \
                  + "/purchases/" + paymentToken
            headers = {'content-type': 'application/json', 'Authorization': token}
            result = requests.post(url, data=serializer.data, headers=headers)
            statusCode = result.status_code

            if statusCode == 200:
                response = result.json()
                purchaseState = response['purchaseState']
                if purchaseState == 0:
                    developerPayload = response['developerPayload']
                    if developerPayload != request.user.username:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                    client.purchasedArticles.add(article)
                    client.save()
                    return Response(status=status.HTTP_200_OK)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            elif statusCode == 401:
                success = self.refreshToken()
                if success:
                    return self.post(request)
                else:
                    return Response(status=status.HTTP_412_PRECONDITION_FAILED)
            else:
                return Response(status=status.HTTP_412_PRECONDITION_FAILED)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

    def getToken(self):
        if BazarToken.objects.all().exists() is True:
            bazarToken = BazarToken.objects.all().first()
            return bazarToken.accessToken
        else:
            success = self.initialToken()
            if success:
                bazarToken = BazarToken.objects.all().first()
                return bazarToken.accessToken
            else:
                return None

    def refreshToken(self):
        if BazarToken.objects.all().exists():
            bazarToken = BazarToken.objects.all().first()
            url = "https://pardakht.cafebazaar.ir/devapi/v2/auth/token/"
            data = dict()
            data['grant_type'] = "refresh_token"
            data['client_secret'] = "pfjAAIMiOeWh1yPXqk9dQ9YRoyWvQwpCOdTTZqzup3AGBTJyEljPNcGb8m68"
            data['client_id'] = "V9hWZVtm0MNqSua0NGjxSbdRTLdmCg76fg57VriA"
            data['refresh_token'] = bazarToken.refreshToken
            result = requests.post(url, data=data)
            if result.status_code == 200:
                response = result.json()
                bazarToken.accessToken = response['access_token']
                bazarToken.tokenType = response['token_type']
                bazarToken.save()
                return True
            else:
                bazarToken.delete()
                return False
        else:
            return False

    def initialToken(self):
        configs = Configs.objects.all().first()
        if BazarToken.objects.all().exists():
            BazarToken.objects.all().first().delete()
        url = "https://pardakht.cafebazaar.ir/devapi/v2/auth/token/"
        data = dict()
        data['grant_type'] = "authorization_code"
        data['code'] = configs.cafeBazarCode
        data['client_secret'] = "pfjAAIMiOeWh1yPXqk9dQ9YRoyWvQwpCOdTTZqzup3AGBTJyEljPNcGb8m68"
        data['client_id'] = "V9hWZVtm0MNqSua0NGjxSbdRTLdmCg76fg57VriA"
        data['redirect_uri'] = "http://5.253.26.156/api/v1/bazar/token/"
        result = requests.post(url, data=data)
        if result.status_code == 200:
            response = result.json()
            accessToken = response['access_token']
            refreshToken = response['refresh_token']
            tokenType = response['token_type']
            BazarToken.objects.create(accessToken=accessToken, refreshToken=refreshToken, tokenType=tokenType)
            return True
        else:
            return False
