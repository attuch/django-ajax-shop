import logging
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from models import *
from django.utils.safestring import mark_safe
from django.utils.html import escape
from django import forms
from django.utils.safestring import mark_safe
import os, Image

class PurchaseCartInline(admin.TabularInline):
    model = PurchaseCart
    max_num = 1

class DiscountInline(admin.TabularInline):
    model = Discount
    max_num = 1

class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'article_count')

    def article_count(self, obj):
        return len(Product.objects.filter(tags=obj))
    article_count.short_description = _('Applied To')

class ProductAdmin(admin.ModelAdmin):
    list_display = ('name','description','price','date_disponibility','primo_piano','number','thumb')
    list_editable = ('price','primo_piano','number','date_disponibility','description')
    inlines = [DiscountInline]

    def preview(self, obj):
        image = "<img src='%s' />" % obj.image.url
        return mark_safe(image)
    preview.short_description = _('Thumbnail')

#class CartObjInline(admin.TabularInline):
    #model = Cart.product.through

class CartAdmin(admin.ModelAdmin):
    list_display = ('__unicode__',)
    inlines = [PurchaseCartInline]

class CartObjAdmin(admin.ModelAdmin):
    list_display = ('product','num','data')

class TagInline(admin.TabularInline):
    model = Tag

class ProductInline(admin.TabularInline):
    model = Product

class DiscountAdmin(admin.ModelAdmin):
    list_display = ('id','discount','product')
    list_editable = ['discount','product']

admin.site.register(Tag, TagAdmin)
admin.site.register(Product, ProductAdmin)
admin.site.register(Cart, CartAdmin)
admin.site.register(CartObj, CartObjAdmin)
admin.site.register(Discount, DiscountAdmin)


