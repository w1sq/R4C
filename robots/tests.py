from io import BytesIO
from datetime import timedelta

import pandas
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from robots.models import Robot


class ProductionReportTests(TestCase):
    def test_download_report_no_data(self):
        response = self.client.get(reverse("download_report"))
        self.assertEqual(response.status_code, 204)

    def test_download_report_outdated_data(self):
        Robot.objects.create(
            model="R2",
            version="D2",
            created=timezone.now() - timedelta(days=10),
        )

        response = self.client.get(reverse("download_report"))
        self.assertEqual(response.status_code, 204)

    def test_download_report_with_data(self):
        mock_data = {
            "R2": {"D2": 1, "A1": 1, "C8": 1, "B1": 1},
            "R3": {"D2": 1, "B1": 1},
            "R4": {"D2": 1, "B1": 1},
        }
        for model, versions in mock_data.items():
            for version, count in versions.items():
                Robot.objects.create(
                    model=model,
                    version=version,
                    created=timezone.now() - timedelta(days=1),
                )

        response = self.client.get(reverse("download_report"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

        tables = pandas.read_excel(BytesIO(response.content), sheet_name=None)
        self.assertEqual(len(tables), len(mock_data))

        for model, versions in mock_data.items():
            self.assertIn(model, tables)
            table = tables[model]
            self.assertEqual(table.shape, (len(versions), 3))
            for i, (version, count) in enumerate(versions.items()):
                self.assertEqual(table.iloc[i, 0], model)
                self.assertEqual(table.iloc[i, 1], version)
                self.assertEqual(table.iloc[i, 2], count)
