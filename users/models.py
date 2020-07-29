from django.db import models
from django.contrib.auth.models import AbstractUser, Group


class CustomUser(AbstractUser):
    is_unknown = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        super(CustomUser, self).save(*args, **kwargs)
        customer_group = Group.objects.get(name='customer')
        self.groups.add(customer_group)
        super(CustomUser, self).save(*args, **kwargs)
