from rest_framework.serializers import (
    Serializer,
    EmailField,
    CharField,
    IntegerField,
    SerializerMethodField,
    ModelSerializer,
    BooleanField,
)

from API.validators import *
from API.models import (Category, Article, ArticlePart, Author, Tag, Configs)


class AuthenticationSerializer(Serializer):
    client_id = CharField(validators=[clientIDValidator])
    client_secret = CharField(validators=[clientSecretValidator])


class UserRegisterSerializer(AuthenticationSerializer):
    email = EmailField()
    password = CharField(validators=[passwordValidator])
    username = CharField(validators=[usernameValidator])


class LoginSerializer(AuthenticationSerializer):
    username = CharField(validators=[usernameValidator])
    password = CharField(validators=[passwordValidator])
    grant_type = CharField(max_length=20)


class LogoutSerializer(AuthenticationSerializer):
    token = CharField(max_length=200)


class RefreshTokenSerializer(AuthenticationSerializer):
    refresh_token = CharField(max_length=255)
    grant_type = CharField(max_length=20)


class ConfigsSerializer(ModelSerializer):
    monencoWebsite = SerializerMethodField()
    monencoWebsiteTitle = SerializerMethodField()
    minCategorySelectCount = SerializerMethodField()
    categories = SerializerMethodField()
    bannerArticles = SerializerMethodField()
    newArticles = SerializerMethodField()
    shareFooter = SerializerMethodField()
    aboutUs = SerializerMethodField()
    username = SerializerMethodField()

    class Meta:
        model = Configs
        fields = [
            'monencoWebsite',
            'monencoWebsiteTitle',
            'minCategorySelectCount',
            'categories',
            'bannerArticles',
            'newArticles',
            'shareFooter',
            'aboutUs',
            'username',
        ]

    def get_monencoWebsite(self, obj):
        return obj.monencoWebsite

    def get_monencoWebsiteTitle(self, obj):
        if self.context['isPersian'] is False:
            return obj.monencoWebsiteTitle
        else:
            return obj.persianMonencoWebsiteTitle

    def get_minCategorySelectCount(self, obj):
        return obj.minCategorySelectCount

    def get_categories(self, obj):
        categories = Category.objects.all()
        return CategorySerializer(categories, many=True, context=self.context).data

    def get_bannerArticles(self, obj):
        client = self.context.get('request').user.client
        articles = Article.objects.filter(isBanner=True, isPersian=self.context['isPersian'], published=True,
                                          category__in=client.favoriteCategories.all()).distinct().order_by(
            '-creationDate')
        return ArticleCompactSerializer(articles, many=True, context=self.context).data

    def get_newArticles(self, obj):
        client = self.context.get('request').user.client
        articles = Article.objects.filter(isPersian=self.context['isPersian'], published=True,
                                          category__in=client.favoriteCategories.all()).order_by('-creationDate')[:10]
        return ArticleCompactSerializer(articles, many=True, context=self.context).data

    def get_shareFooter(self, obj):
        if self.context['isPersian'] is False:
            return obj.shareFooter
        else:
            return obj.persianShareFooter

    def get_aboutUs(self, obj):
        if self.context['isPersian'] is False:
            return obj.aboutUs
        else:
            return obj.persianAboutUs

    def get_username(self, obj):
        return self.context['request'].user.username


class ToggleSerializer(Serializer):
    id = IntegerField()
    newState = BooleanField()


class ToggleSetSerializer(Serializer):
    toggleSet = ToggleSerializer(many=True)


class CategorySerializer(ModelSerializer):
    name = SerializerMethodField()
    icon = SerializerMethodField()
    isFavorite = SerializerMethodField()

    class Meta:
        model = Category
        fields = [
            'name',
            'icon',
            'id',
            'isFavorite'
        ]

    def get_name(self, obj):
        isPersian = self.context['isPersian']
        if isPersian:
            return obj.persianName
        else:
            return obj.name

    def get_isFavorite(self, obj):
        request = self.context['request']
        return obj in request.user.client.favoriteCategories.all()

    def get_icon(self, obj):
        try:
            request = self.context['request']
            image_url = obj.icon.url
            to_return = request.build_absolute_uri(image_url)
            return to_return
        except:
            return ""


class ArticleCompactSerializer(ModelSerializer):
    image = SerializerMethodField()
    isBookmarked = SerializerMethodField()
    creationDate = SerializerMethodField()
    tags = SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'title',
            'image',
            'leadText',
            'isBookmarked',
            'id',
            'creationDate',
            'tags',
        ]

    def get_image(self, obj):
        try:
            request = self.context['request']
            image_url = obj.image.url
            to_return = request.build_absolute_uri(image_url)
            return to_return
        except:
            return ""

    def get_isBookmarked(self, obj):
        request = self.context['request']
        return obj in request.user.client.bookmarkedArticles.all()

    def get_creationDate(self, obj):
        return obj.creationDate.date()

    def get_tags(self, obj):
        tags = obj.tags.all()
        return TagSerializer(tags, many=True, context=self.context).data


class ArticleSerializer(ModelSerializer):
    parts = SerializerMethodField()
    image = SerializerMethodField()
    author = SerializerMethodField()
    category = SerializerMethodField()
    creationDate = SerializerMethodField()
    tags = SerializerMethodField()
    isBookmarked = SerializerMethodField()
    relatedArticles = SerializerMethodField()
    purchasable = SerializerMethodField()
    purchased = SerializerMethodField()
    price = SerializerMethodField()

    class Meta:
        model = Article
        fields = [
            'parts',
            'title',
            'leadText',
            'id',
            'image',
            'author',
            'category',
            'creationDate',
            'tags',
            'isBookmarked',
            'relatedArticles',
            'purchasable',
            'purchased',
            'price',
            'cafeBazarPaymentId',
        ]

    def get_parts(self, obj):
        client = self.context['request'].user.client
        if obj.price == 0 or obj in client.purchasedArticles.all():
            parts = ArticlePart.objects.filter(article=obj).order_by('order')
            return ArticlePartSerializer(parts, many=True, context=self.context).data
        return None

    def get_image(self, obj):
        try:
            request = self.context['request']
            image_url = obj.image.url
            to_return = request.build_absolute_uri(image_url)
            return to_return
        except:
            return ""

    def get_author(self, obj):
        return AuthorSerializer(obj.author, context=self.context).data

    def get_category(self, obj):
        return CategorySerializer(obj.category, context=self.context).data

    def get_creationDate(self, obj):
        return obj.creationDate.date()

    def get_tags(self, obj):
        tags = obj.tags.all()
        return TagSerializer(tags, many=True, context=self.context).data

    def get_isBookmarked(self, obj):
        request = self.context['request']
        return obj in request.user.client.bookmarkedArticles.all()

    def get_relatedArticles(self, obj):
        return ""

    def get_purchasable(self, obj):
        return obj.price > 0

    def get_purchased(self, obj):
        client = self.context['request'].user.client
        return obj in client.purchasedArticles.all()

    def get_price(self, obj):
        return obj.price


class ArticlePartSerializer(ModelSerializer):
    image = SerializerMethodField()

    class Meta:
        model = ArticlePart
        fields = [
            'type',
            'title',
            'image',
            'content',
        ]

    def get_image(self, obj):
        try:
            request = self.context['request']
            image_url = obj.image.url
            to_return = request.build_absolute_uri(image_url)
            return to_return
        except:
            return ""


class TagSerializer(ModelSerializer):
    name = SerializerMethodField()

    class Meta:
        model = Tag
        fields = [
            'name',
        ]

    def get_name(self, obj):
        isPersian = self.context['isPersian']
        if isPersian:
            return obj.persianName
        else:
            return obj.name


class AuthorSerializer(ModelSerializer):
    name = SerializerMethodField()

    class Meta:
        model = Author
        fields = [
            'name',
        ]

    def get_name(self, obj):
        isPersian = self.context['isPersian']
        if isPersian:
            return obj.publicPersianName
        else:
            return obj.publicName


class PurchaseArticleSerializer(Serializer):
    articleID = IntegerField(required=True)
    platform = CharField(required=True)


class PaymentCheckSerializer(Serializer):
    paymentId = CharField(required=True, max_length=255)
    paymentToken = CharField(required=True, max_length=255)
