from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from core.models.base import BaseModel

class user(BaseModel, AbstractBaseUser, PermissionsMixin):
    Clerk_id = models.CharField(max_length=50, unique=True)
    email = models.EmailField(max_length=50, unique=True)

    first_name = models.CharField(max_length=50, default = "", blank=True)
    last_name = models.CharField(max_length=50, default = "", blank=True)


    USERNAME_FIELD = "email"
    REQUIRED_FIELD = ["clerk_id"]

    def __str__(self):
        return f"{self.email}({self.Clerk_id})"
    