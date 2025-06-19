# app/admin.py
from django.contrib import admin
from .models import Data  # Must match your model class name (PascalCase)

admin.site.register(Data)