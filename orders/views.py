from django.http import JsonResponse
from django.core.exceptions import ValidationError

from .models import Order
from customers.models import Customer


def place_order(request):
    if request.method == "POST":
        customer_email = request.POST.get("email")
        robot_serial = request.POST.get("robot_serial")

        if not customer_email or not robot_serial:
            return JsonResponse(
                {"error": "Email and robot serial are required."}, status=400
            )

        try:
            customer, created = Customer.objects.get_or_create(email=customer_email)

            Order.objects.create(customer=customer, robot_serial=robot_serial)

            return JsonResponse({"message": "Order placed successfully!"}, status=201)

        except ValidationError:
            return JsonResponse({"error": "Invalid data provided."}, status=400)

        except Exception:
            return JsonResponse(
                {"error": "An error occurred while placing the order."}, status=500
            )

    return JsonResponse({"error": "Invalid request method."}, status=405)
