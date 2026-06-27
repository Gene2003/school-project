# Web-Based Supply Chain Platform

A web-based agricultural supply chain platform that connects **farmers,
wholesalers, retailers and consumers** in a single marketplace — with secure
payments, automated commission/referral tracking, and real-time SMS & email
notifications.

Built for the BCT 2315 Group Five proposal, Multimedia University of Kenya.

- **Backend:** Django REST Framework (Python), JWT auth
- **Frontend:** React.js (Vite)
- **Database:** SQLite for development, PostgreSQL in production
- **Integrations:** Paystack (payments & split), Africa's Talking (SMS), SendGrid (email)

> The third-party integrations run in **simulation mode** when their API keys
> are not set, so the entire checkout → payment → commission → notification flow
> works out-of-the-box for development and demos. Add the real keys in
> `backend/.env` to go live.

---

## Project structure

```
project/
├── backend/                 # Django REST Framework API
│   ├── config/              # settings, root urls, wsgi/asgi
│   ├── users/               # role-based accounts, JWT auth, referrals
│   ├── products/            # product listing & management
│   ├── orders/              # orders & order items (checkout)
│   ├── payments/            # Paystack integration & split payments
│   ├── commissions/         # platform fee & referral tracker
│   ├── notifications/       # Africa's Talking SMS + SendGrid email
│   ├── manage.py
│   └── requirements.txt
└── frontend/                # React.js (Vite) single-page app
    └── src/
        ├── api/             # axios client + grouped service calls
        ├── components/      # Navbar, ProductCard, ProtectedRoute, …
        ├── context/         # AuthContext, CartContext
        └── pages/           # marketplace, checkout, dashboards, admin
```

---

## Getting started

### 1. Backend (Django)

```bash
cd backend
# create / activate a virtualenv, then:
venv/Scripts/python -m pip install -r requirements.txt   # Windows
# python -m pip install -r requirements.txt              # macOS/Linux

python manage.py migrate
python manage.py seed_demo        # demo users + products (optional)
python manage.py createsuperuser  # for the Django admin (optional)
python manage.py runserver        # http://127.0.0.1:8000
```

API root: <http://127.0.0.1:8000/> · Django admin: <http://127.0.0.1:8000/admin/>

### 2. Frontend (React)

```bash
cd frontend
npm install
npm run dev                       # http://localhost:5173
```

The Vite dev server proxies `/api` and `/media` to Django on port 8000.

---

## Demo accounts

After running `seed_demo`, all accounts use the password **`Password123`**:

| Role        | Email                    |
| ----------- | ------------------------ |
| Admin       | admin@agric.co.ke        |
| Farmer      | farmer@agric.co.ke       |
| Wholesaler  | wholesaler@agric.co.ke   |
| Retailer    | retailer@agric.co.ke     |
| Consumer    | consumer@agric.co.ke     |

---

## Key API endpoints

| Area          | Endpoint                                   |
| ------------- | ------------------------------------------ |
| Register      | `POST /api/auth/register/`                 |
| Login (JWT)   | `POST /api/auth/login/`                    |
| Profile       | `GET/PATCH /api/auth/me/`                  |
| Products      | `GET/POST /api/products/`                  |
| Checkout      | `POST /api/orders/`                        |
| Seller sales  | `GET /api/orders/sales/`                   |
| Init payment  | `POST /api/payments/initialize/`           |
| Verify payment| `POST /api/payments/verify/`               |
| Commissions   | `GET /api/commissions/`                    |
| Notifications | `GET /api/notifications/`                  |
| Admin stats   | `GET /api/auth/stats/`                     |

---

## Environment variables (`backend/.env`)

See `backend/.env.example`. Leave the third-party keys blank to use simulation
mode; fill them in to enable live Paystack payments, Africa's Talking SMS and
SendGrid email. Set `DATABASE_URL` to a `postgres://…` URL to use PostgreSQL.
