from django.contrib import admin
from .models import Client

@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display  = ('last_name','first_name','phone','email','passport_data','registration_date')
    search_fields = ('first_name','last_name','phone','email','passport_data')
    list_per_page = 20
