"""Seed the platform with demo users, categories and product listings."""

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from products.models import Category, Product

User = get_user_model()

DEMO_PASSWORD = 'Password123'

USERS = [
    ('admin@agric.co.ke', 'Platform Admin', User.Role.ADMIN, '0700000000', 'Nairobi'),
    ('farmer@agric.co.ke', 'Jane Wanjiru', User.Role.FARMER, '0711111111', 'Nyeri'),
    ('wholesaler@agric.co.ke', 'Otieno Supplies', User.Role.WHOLESALER, '0722222222', 'Eldoret'),
    ('retailer@agric.co.ke', 'Mama Mboga Mart', User.Role.RETAILER, '0733333333', 'Nakuru'),
    ('consumer@agric.co.ke', 'Brian Kamau', User.Role.CONSUMER, '0744444444', 'Nairobi'),
]

CATEGORIES = ['Vegetables', 'Fruits', 'Grains & Cereals', 'Dairy', 'Tubers', 'Legumes']

PRODUCTS = [
    ('farmer@agric.co.ke', 'Vegetables', 'Fresh Sukuma Wiki (Kale)', 30, 'bunch', 200, 'Nyeri'),
    ('farmer@agric.co.ke', 'Fruits', 'Sweet Bananas', 120, 'bunch', 80, 'Nyeri'),
    ('farmer@agric.co.ke', 'Tubers', 'Irish Potatoes', 3500, 'bag', 40, 'Nyeri'),
    ('farmer@agric.co.ke', 'Vegetables', 'Ripe Tomatoes', 90, 'kg', 150, 'Nyeri'),
    ('wholesaler@agric.co.ke', 'Grains & Cereals', 'Maize (90kg bag)', 4200, 'bag', 60, 'Eldoret'),
    ('wholesaler@agric.co.ke', 'Legumes', 'Yellow Beans', 130, 'kg', 500, 'Eldoret'),
    ('wholesaler@agric.co.ke', 'Dairy', 'Fresh Milk', 60, 'litre', 300, 'Eldoret'),
    ('farmer@agric.co.ke', 'Fruits', 'Hass Avocados', 15, 'piece', 1000, 'Nyeri'),
]


class Command(BaseCommand):
    help = 'Seed demo users, categories and products (idempotent).'

    def handle(self, *args, **options):
        for email, name, role, phone, location in USERS:
            user, created = User.objects.get_or_create(
                email=email,
                defaults={'full_name': name, 'role': role,
                          'phone_number': phone, 'location': location},
            )
            if created:
                user.set_password(DEMO_PASSWORD)
                if role == User.Role.ADMIN:
                    user.is_staff = True
                    user.is_superuser = True
                user.save()
                self.stdout.write(self.style.SUCCESS(f'  + user {email}'))

        categories = {}
        for name in CATEGORIES:
            categories[name], _ = Category.objects.get_or_create(name=name)

        for email, cat, name, price, unit, qty, location in PRODUCTS:
            seller = User.objects.get(email=email)
            Product.objects.get_or_create(
                seller=seller, name=name,
                defaults={
                    'category': categories.get(cat),
                    'price': price, 'unit': unit,
                    'quantity_available': qty, 'location': location,
                    'description': f'High quality {name.lower()} sourced directly from the farm.',
                },
            )

        self.stdout.write(self.style.SUCCESS(
            f'\nDemo data ready. All accounts use password: {DEMO_PASSWORD}\n'
            f'  admin@agric.co.ke  | farmer@agric.co.ke | wholesaler@agric.co.ke\n'
            f'  retailer@agric.co.ke | consumer@agric.co.ke'
        ))
