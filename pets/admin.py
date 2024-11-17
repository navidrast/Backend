# pets/admin.py

from django.contrib import admin
from .models import Pet, PetHealthRecord

class PetHealthRecordInline(admin.TabularInline):
    model = PetHealthRecord
    extra = 1

@admin.register(Pet)
class PetAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'breed', 'size', 
                   'gender', 'is_sterilized')
    list_filter = ('gender', 'is_sterilized','size')
    search_fields = ('name', 'owner__username', 'breed')
    inlines = [PetHealthRecordInline]

@admin.register(PetHealthRecord)
class PetHealthRecordAdmin(admin.ModelAdmin):
    list_display = ('pet', 'date', 'title')
    list_filter = ('date',)
    search_fields = ('pet__name', 'title', 'description')