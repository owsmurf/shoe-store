from django.contrib import admin
from .models import Role, User, Category, Manufacturer, Supplier, Unit, Product, PickupPoint, Order, OrderItem

admin.site.register(Role)
admin.site.register(User)
admin.site.register(Category)
admin.site.register(Manufacturer)
admin.site.register(Supplier)
admin.site.register(Unit)
admin.site.register(Product)
admin.site.register(PickupPoint)
admin.site.register(Order)
admin.site.register(OrderItem)
