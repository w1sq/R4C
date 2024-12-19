from typing import Union
from datetime import timedelta

import os
import pandas
from django.http import HttpResponse
from django.utils import timezone

from .models import Robot


def get_production_data(
    model: Union[str, None] = None,
    version: Union[str, None] = None,
    start_date: Union[timezone.datetime, None] = None,
    end_date: Union[timezone.datetime, None] = None,
) -> dict[str, dict[str, int]]:
    """
    Get production data as dict with optional filters.
    """
    if start_date is None or end_date is None:
        end_date = timezone.now()
        start_date = end_date - timedelta(days=7)

    robots = Robot.objects.filter(created__range=(start_date, end_date))

    if model is not None:
        robots = robots.filter(model=model)
    if version is not None:
        robots = robots.filter(version=version)

    # Structure the data
    data = {}
    for robot in robots:
        model = robot.model
        version = robot.version
        if model not in data:
            data[model] = {}
        if version not in data[model]:
            data[model][version] = 0
        data[model][version] += 1

    return data


def download_production_report(request):
    """
    Download production report as Excel file.
    """
    filename = "production_report.xlsx"

    production_data = get_production_data()

    if not production_data:
        return HttpResponse("No production data available.", status=204)

    with pandas.ExcelWriter(filename, engine="openpyxl") as writer:
        for model, versions in production_data.items():
            df = pandas.DataFrame(
                [(model, version, count) for version, count in versions.items()],
                columns=["Модель", "Версия", "Количество за неделю"],
            )
            df.to_excel(writer, sheet_name=model, index=False)

    with open(filename, "rb") as f:
        response = HttpResponse(
            f.read(),
            content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
        response["Content-Disposition"] = f'attachment; filename="{filename}"'

    os.remove(filename)

    return response
