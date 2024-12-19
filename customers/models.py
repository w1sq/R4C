import re

from django.db import models
from django.core.exceptions import ValidationError


class Customer(models.Model):
    email = models.EmailField(max_length=255, unique=True, blank=False, null=False)

    def clean(self):
        """
        Validate the email format.
        """
        email_regex = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_regex, self.email):
            raise ValidationError("Invalid email format.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
