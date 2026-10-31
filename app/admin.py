from django.contrib import admin
from .models import CustomUser,Category,Product,Cart,CartItem,Order,OrderItem,Address,ProductImage,Brand,Profile,DeliveryBoy
# Register your models here.

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

CustomUser = get_user_model()

class CustomUserAdmin(UserAdmin):
    model = CustomUser

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'is_manager', 'is_deliveryboy', 'status')}),  # Added status
        (_('Permissions'), {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_manager', 'is_deliveryboy', 'status'),  # Added status
        }),
    )

    list_display = ('username', 'email', 'first_name', 'last_name', 'status', 'is_staff', 'is_manager', 'is_deliveryboy')  # Added status
    search_fields = ('username', 'email', 'first_name', 'last_name', 'status')  # Added status to search
    ordering = ('username',)

admin.site.register(CustomUser, CustomUserAdmin)

admin.site.register(Category)
class ProductPage(admin.ModelAdmin):
    exclude = ['brand']
admin.site.register(Product,ProductPage)
admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Address)
admin.site.register(ProductImage)
admin.site.register(Brand)
admin.site.register(Profile)
admin.site.register(DeliveryBoy)


