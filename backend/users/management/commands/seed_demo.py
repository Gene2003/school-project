"""Seed the platform with demo users, categories and product listings."""

from pathlib import Path

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files import File
from django.core.management.base import BaseCommand

from products.models import Category, Product

User = get_user_model()

DEMO_PASSWORD = 'Password123'

# Source images shipped with the repo (version-controlled, unlike media/).
SEED_ASSETS = Path(settings.BASE_DIR) / 'seed_assets'

USERS = [
    ('admin@agric.co.ke', 'Platform Admin', User.Role.ADMIN, '0700000000', 'Nairobi'),
    ('farmer@agric.co.ke', 'Jane Wanjiru', User.Role.FARMER, '0711111111', 'Nyeri'),
    ('wholesaler@agric.co.ke', 'Otieno Supplies', User.Role.WHOLESALER, '0722222222', 'Eldoret'),
    ('retailer@agric.co.ke', 'Mama Mboga Mart', User.Role.RETAILER, '0733333333', 'Nakuru'),
    ('consumer@agric.co.ke', 'Brian Kamau', User.Role.CONSUMER, '0744444444', 'Nairobi'),
]

CATEGORIES = ['Vegetables', 'Fruits', 'Grains & Cereals', 'Dairy', 'Tubers', 'Legumes']

# email, category, name, price, unit, qty, location, image filename (in seed_assets)
PRODUCTS = [
    ('farmer@agric.co.ke', 'Vegetables', 'Fresh Sukuma Wiki (Kale)', 30, 'bunch', 200, 'Nyeri', 'market-greens.jpg'),
    ('farmer@agric.co.ke', 'Fruits', 'Sweet Bananas', 120, 'bunch', 80, 'Nyeri', 'banana.jpg'),
    ('farmer@agric.co.ke', 'Tubers', 'Irish Potatoes', 3500, 'bag', 40, 'Nyeri', 'potatoes.jpg'),
    ('farmer@agric.co.ke', 'Vegetables', 'Ripe Tomatoes', 90, 'kg', 150, 'Nyeri', 'tomatoes.jpg'),
    ('farmer@agric.co.ke', 'Vegetables', 'Red Onions', 110, 'kg', 250, 'Nyeri', 'onions.jpg'),
    ('farmer@agric.co.ke', 'Fruits', 'Hass Avocados', 15, 'piece', 1000, 'Nyeri', 'avocado.jpg'),
    ('farmer@agric.co.ke', 'Dairy', 'Fresh Eggs (tray of 30)', 450, 'crate', 120, 'Nyeri', 'eggs.jpg'),
    ('wholesaler@agric.co.ke', 'Grains & Cereals', 'Maize (90kg bag)', 4200, 'bag', 60, 'Eldoret', 'maize.jpg'),
    ('wholesaler@agric.co.ke', 'Grains & Cereals', 'Pishori Rice (25kg)', 3800, 'bag', 90, 'Eldoret', 'rice.jpg'),
    ('wholesaler@agric.co.ke', 'Legumes', 'Yellow Beans', 130, 'kg', 500, 'Eldoret', None),
    ('wholesaler@agric.co.ke', 'Dairy', 'Fresh Milk', 60, 'litre', 300, 'Eldoret', None),
]


class Command(BaseCommand):
    help = 'Seed demo users, categories and products with images (idempotent).'

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

        for email, cat, name, price, unit, qty, location, image_file in PRODUCTS:
            seller = User.objects.get(email=email)
            product, _ = Product.objects.get_or_create(
                seller=seller, name=name,
                defaults={
                    'category': categories.get(cat),
                    'price': price, 'unit': unit,
                    'quantity_available': qty, 'location': location,
                    'description': f'High quality {name.lower()} sourced directly from the farm.',
                },
            )
            # Attach the product image if one is provided and not already set.
            if image_file and not product.image:
                source = SEED_ASSETS / image_file
                if source.exists():
                    with source.open('rb') as fh:
                        product.image.save(image_file, File(fh), save=True)
                    self.stdout.write(f'    · image set for {name}')
                else:
                    self.stdout.write(self.style.WARNING(f'    ! missing image {source}'))

        self.stdout.write(self.style.SUCCESS(
            f'\nDemo data ready. All accounts use password: {DEMO_PASSWORD}\n'
            f'  admin@agric.co.ke  | farmer@agric.co.ke | wholesaler@agric.co.ke\n'
            f'  retailer@agric.co.ke | consumer@agric.co.ke'
        ))
