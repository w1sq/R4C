import json
from datetime import datetime

from django.utils import timezone
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.db import IntegrityError, DatabaseError
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from .models import Robot


@csrf_exempt
@require_http_methods(["POST"])
def create_robot(request):
    try:
        # Parse JSON data
        data = json.loads(request.body)

        # Validate required fields
        required_fields = ["model", "version", "created"]
        if not all(field in data for field in required_fields):
            return JsonResponse({"error": "Missing required fields"}, status=400)

        # Validate model and version length
        if len(data["model"]) > 2 or len(data["version"]) > 2:
            return JsonResponse(
                {"error": "Model and version must be not longer than 2 characters"},
                status=400,
            )

        # Validate date format
        try:
            created_date = timezone.make_aware(
                datetime.strptime(data["created"], "%Y-%m-%d %H:%M:%S")
            )
        except ValueError:
            return JsonResponse(
                {"error": "Invalid date format. Use YYYY-MM-DD HH:MM:SS"},
                status=400,
            )

        # Create robot record
        try:
            robot = Robot.objects.create(
                serial=f"{data['model']}-{data['version']}",
                model=data["model"],
                version=data["version"],
                created=created_date,
            )
        except (ValidationError, IntegrityError, DatabaseError) as e:
            return JsonResponse({"error": str(e)}, status=500)

        return JsonResponse(
            {
                "message": "Robot created successfully",
                "robot": {
                    "serial": robot.serial,
                    "model": robot.model,
                    "version": robot.version,
                    "created": robot.created.strftime("%Y-%m-%d %H:%M:%S"),
                },
            },
            status=201,
        )

    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON format"}, status=400)
    except Exception:
        return JsonResponse({"error": "Internal server error"}, status=500)
