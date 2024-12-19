import os

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail

from .models import Robot
from orders.models import Order


@receiver(post_save, sender=Robot)
def notify_customers_when_robot_available(sender, instance, created, **kwargs):
    if created:
        orders = Order.objects.filter(robot_serial=instance.serial)
        for order in orders:
            send_robot_availability_email(order, instance)


def send_robot_availability_email(order: Order, robot: Robot):
    subject = "Ваш заказ на робота доступен"
    message = f"Добрый день!\nНедавно вы интересовались нашим роботом модели {robot.model}, версии {robot.version}.\nЭтот робот теперь в наличии. Если вам подходит этот вариант - пожалуйста, свяжитесь с нами."
    send_mail(
        subject,
        message,
        os.getenv("EMAIL_HOST_USER"),
        [order.customer.email],
        fail_silently=False,
    )
