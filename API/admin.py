from django.contrib import admin
from API.models import *

admin.site.register(Client)
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Tag)


class ArticleAdmin(admin.ModelAdmin):
    def Title(self, obj):
        return obj.title

    def Author(self, obj):
        if obj.isPersian:
            return obj.author.publicPersianName
        else:
            return obj.author.publicName

    def Price(self, obj):
        return str(obj.price) + " T"

    def Status(self, obj):
        if obj.published:
            return "Published"
        else:
            return "Draft"

    def Category(self, obj):
        if obj.isPersian:
            return obj.category.persianName
        else:
            return obj.category.name

    def Lang(self, obj):
        if obj.isPersian:
            return "FA"
        else:
            return "EN"

    list_display = ("Title", "Author", "Price", "Status", "Category", "Lang")


admin.site.register(Article, ArticleAdmin)
admin.site.register(BazarToken)

class ArticlePartAdmin(admin.ModelAdmin):
    def article(self, obj):
        return obj.article.title

    def Part_Title(self, obj):
        if obj.title is not None and str(obj.title) != "":
            return obj.title
        else:
            return "No Title"

    def Order(self, obj):
        return obj.order

    def Type(self, obj):
        if obj.type == 1:
            return "Text"
        else:
            return "Image"

    list_display = ("article", 'Part_Title', 'Order', 'Type')
    list_filter = (
        ('article', admin.RelatedOnlyFieldListFilter),
    )


admin.site.register(ArticlePart, ArticlePartAdmin)
admin.site.register(Configs)
