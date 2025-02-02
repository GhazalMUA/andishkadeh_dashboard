from django.contrib import admin
from .models import Continent, Region, ResearchArea, ResearchCenter, Order, OrderDetail, Numbering, Status, OrderResult, TimeRange

admin.site.register(Continent)
admin.site.register(Region)
admin.site.register(ResearchCenter)
admin.site.register(Order)
admin.site.register(OrderDetail)
admin.site.register(Numbering)
admin.site.register(Status)
admin.site.register(OrderResult)
admin.site.register(TimeRange)


@admin.register(ResearchArea)
class ResearchAreaAdmin(admin.ModelAdmin):
    list_display = ('name',)  # Assuming 'name' is the field you want to display
    ordering = ['name']