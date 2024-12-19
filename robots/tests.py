import json

from django.test import TestCase, Client
from django.urls import reverse

from .models import Robot


class RobotAPITests(TestCase):
    def setUp(self):
        self.client = Client()
        self.create_url = reverse("robots:create_robot")

    def test_create_valid_robot(self):
        valid_payload = {
            "model": "R2",
            "version": "D2",
            "created": "2022-12-31 23:59:59",
        }
        response = self.client.post(
            self.create_url,
            data=json.dumps(valid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Robot.objects.count(), 1)
        robot = Robot.objects.first()
        self.assertEqual(robot.serial, "R2-D2")

    def test_invalid_date_format(self):
        invalid_payload = {
            "model": "R2",
            "version": "D2",
            "created": "2022-31-12 23:59:59",
        }
        response = self.client.post(
            self.create_url,
            data=json.dumps(invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Robot.objects.count(), 0)

    def test_create_invalid_model_length(self):
        invalid_payload = {
            "model": "R2D",  # Too long
            "version": "D2",
            "created": "2022-12-31 23:59:59",
        }
        response = self.client.post(
            self.create_url,
            data=json.dumps(invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Robot.objects.count(), 0)

    def test_invalid_json(self):
        response = self.client.post(
            self.create_url, data="invalid json", content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Robot.objects.count(), 0)

    def test_missing_fields(self):
        invalid_payload = {
            "model": "R2",
            # missing version and created
        }
        response = self.client.post(
            self.create_url,
            data=json.dumps(invalid_payload),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Robot.objects.count(), 0)
