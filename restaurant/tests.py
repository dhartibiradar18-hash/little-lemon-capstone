from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .models import Booking, Menu


class ModelTests(TestCase):
    def test_menu_str(self):
        item = Menu.objects.create(title="IceCream", price=Decimal("80.00"), inventory=100)
        self.assertEqual(str(item), "IceCream : 80.00")

    def test_booking_str(self):
        booking = Booking.objects.create(
            name="Alice", no_of_guests=4, booking_date="2026-11-01T19:00:00Z"
        )
        self.assertIn("Alice", str(booking))


class StaticPageTests(TestCase):
    def test_home_page_served(self):
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "restaurant/index.html")
        self.assertContains(response, "Little Lemon")


class AuthTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_registration_creates_user_and_returns_token(self):
        response = self.client.post(
            "/api/registration/",
            {"username": "chef", "email": "chef@example.com", "password": "Str0ng-Passw0rd!"},
            format="json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertIn("token", response.data)
        self.assertNotIn("password", response.data)
        self.assertTrue(User.objects.filter(username="chef").exists())

    def test_registration_rejects_weak_password(self):
        response = self.client.post(
            "/api/registration/",
            {"username": "weak", "password": "123"},
            format="json",
        )
        self.assertEqual(response.status_code, 400)

    def test_token_login(self):
        User.objects.create_user("waiter", password="Str0ng-Passw0rd!")
        response = self.client.post(
            "/api/token/login/",
            {"username": "waiter", "password": "Str0ng-Passw0rd!"},
            format="json",
        )
        self.assertEqual(response.status_code, 200)
        self.assertIn("token", response.data)

    def test_token_login_wrong_password(self):
        User.objects.create_user("waiter", password="Str0ng-Passw0rd!")
        response = self.client.post(
            "/api/token/login/", {"username": "waiter", "password": "nope"}, format="json"
        )
        self.assertEqual(response.status_code, 400)


class MenuApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("owner", password="Str0ng-Passw0rd!")
        self.token = Token.objects.create(user=self.user)
        self.item = Menu.objects.create(title="Greek Salad", price=Decimal("12.50"), inventory=20)

    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_list_menu_is_public(self):
        response = self.client.get("/api/menu/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["title"], "Greek Salad")

    def test_retrieve_single_item(self):
        response = self.client.get(f"/api/menu/{self.item.pk}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["title"], "Greek Salad")

    def test_create_requires_auth(self):
        response = self.client.post(
            "/api/menu/", {"title": "Pasta", "price": "10.00", "inventory": 5}, format="json"
        )
        self.assertEqual(response.status_code, 401)

    def test_create_with_token(self):
        self.auth()
        response = self.client.post(
            "/api/menu/", {"title": "Pasta", "price": "10.00", "inventory": 5}, format="json"
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Menu.objects.count(), 2)

    def test_create_rejects_negative_price(self):
        self.auth()
        response = self.client.post(
            "/api/menu/", {"title": "Bad", "price": "-1.00", "inventory": 5}, format="json"
        )
        self.assertEqual(response.status_code, 400)

    def test_update_and_delete_with_token(self):
        self.auth()
        url = f"/api/menu/{self.item.pk}/"
        response = self.client.put(
            url, {"title": "Greek Salad", "price": "13.00", "inventory": 18}, format="json"
        )
        self.assertEqual(response.status_code, 200)
        self.item.refresh_from_db()
        self.assertEqual(self.item.price, Decimal("13.00"))
        response = self.client.delete(url)
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Menu.objects.count(), 0)


class BookingApiTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user("guest", password="Str0ng-Passw0rd!")
        self.token = Token.objects.create(user=self.user)
        self.payload = {
            "name": "Maria",
            "no_of_guests": 3,
            "booking_date": "2026-12-24T19:30:00Z",
        }

    def auth(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {self.token.key}")

    def test_bookings_require_auth(self):
        self.assertEqual(self.client.get("/api/bookings/").status_code, 401)
        self.assertEqual(self.client.post("/api/bookings/", self.payload, format="json").status_code, 401)

    def test_create_and_list_booking(self):
        self.auth()
        response = self.client.post("/api/bookings/", self.payload, format="json")
        self.assertEqual(response.status_code, 201)
        response = self.client.get("/api/bookings/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["name"], "Maria")

    def test_invalid_guest_count(self):
        self.auth()
        bad = dict(self.payload, no_of_guests=0)
        response = self.client.post("/api/bookings/", bad, format="json")
        self.assertEqual(response.status_code, 400)

    def test_update_and_delete_booking(self):
        self.auth()
        created = self.client.post("/api/bookings/", self.payload, format="json")
        url = f"/api/bookings/{created.data['id']}/"
        response = self.client.put(url, dict(self.payload, no_of_guests=6), format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(Booking.objects.get(pk=created.data["id"]).no_of_guests, 6)
        self.assertEqual(self.client.delete(url).status_code, 204)
        self.assertEqual(Booking.objects.count(), 0)
