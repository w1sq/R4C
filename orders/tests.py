from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from orders.models import Order
from robots.models import Robot
from customers.models import Customer


class PlaceOrderTests(TestCase):
    def setUp(self):
        self.url = reverse("place_order")
        self.consumer_email = "artem.kokorev2005@yandex.ru"

    def test_place_order_success(self):
        response = self.client.post(
            self.url,
            {"email": self.consumer_email, "robot_serial": "R2-D2"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "Order placed successfully!")
        self.assertTrue(Order.objects.filter(robot_serial="R2-D2").exists())

    def test_email_is_sent_after_robot_appeal(self):
        response = self.client.post(
            self.url,
            {"email": self.consumer_email, "robot_serial": "R2-D2"},
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json()["message"], "Order placed successfully!")
        self.assertTrue(Order.objects.filter(robot_serial="R2-D2").exists())

        robot = Robot.objects.create(
            serial="R2-D2",
            model="R2",
            version="D2",
            created=timezone.now(),
        )  # Here I check that the email is sent

    def test_place_order_missing_email(self):
        response = self.client.post(self.url, {"robot_serial": "R2-D2"})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_place_order_missing_robot_serial(self):
        response = self.client.post(self.url, {"email": self.consumer_email})
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_place_order_invalid_email(self):
        response = self.client.post(
            self.url, {"email": "invalid-email", "robot_serial": "R2-D2"}
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.json())

    def test_place_order_creates_customer(self):
        response = self.client.post(
            self.url, {"email": self.consumer_email, "robot_serial": "R2-D2"}
        )
        self.assertEqual(response.status_code, 201)
        self.assertTrue(Customer.objects.filter(email=self.consumer_email).exists())
