from django.contrib import admin

from .models import Category, Product


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'seller', 'price', 'unit', 'quantity_available', 'is_active')
    list_filter = ('is_active', 'unit', 'category')
    search_fields = ('name', 'description', 'seller__email')
    autocomplete_fields = ('seller',)
