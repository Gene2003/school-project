"""Product listings and their categories."""

from django.conf import settings
from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=90, unique=True, blank=True)

    class Meta:
        verbose_name_plural = 'categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Product(models.Model):
    """A produce listing posted by a farmer or wholesaler."""

    class Unit(models.TextChoices):
        KG = 'kg', 'Kilogram'
        BAG = 'bag', 'Bag'
        CRATE = 'crate', 'Crate'
        PIECE = 'piece', 'Piece'
        LITRE = 'litre', 'Litre'
        BUNCH = 'bunch', 'Bunch'

    seller = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='products'
    )
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products'
    )
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    unit = models.CharField(max_length=10, choices=Unit.choices, default=Unit.KG)
    quantity_available = models.PositiveIntegerField(default=0)
    location = models.CharField(max_length=120, blank=True)
    image = models.ImageField(upload_to='products/', null=True, blank=True)
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.price}/{self.unit}'

    @property
    def in_stock(self):
        return self.quantity_available > 0
