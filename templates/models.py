from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.db.models.signals import post_save
from django.dispatch import receiver



class CustomUserManager(BaseUserManager):
    """Define a model manager for CustomUser model with both email and username authentication."""

    def _create_user(self, email, username, password=None, **extra_fields):
        """Create and save a CustomUser with the given email, username, and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(email=email, username=username, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, username, password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        """Create and save a SuperUser with the given email, username, and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, username, password, **extra_fields)

class CustomUser(AbstractUser):
    username = models.CharField(_('username'), max_length=150, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    is_manager = models.BooleanField('Is manager', default=False)
    is_deliveryboy = models.BooleanField('Is deliveryboy', default=False)


    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()
    



class Category(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

# Product Model
class Product(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, null=True, blank=True)  # Add this
    discount = models.PositiveIntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    stock_quantity = models.PositiveIntegerField(default=0)

    def __str__(self):
        return self.name




class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='static/products/images/')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"Image for {self.product.name}"


class Cart(models.Model):
    user=models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at=models.DateTimeField(auto_now_add=True)
     
    def __str__(self):
        return self.user.username

class CartItem(models.Model):
    cart=models.ForeignKey(Cart, on_delete=models.CASCADE)
    product=models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=0)
    created_at=models.DateTimeField(auto_now_add=True)



class Order(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=10)
    location = models.CharField(max_length=100, null=True, blank=True)  # New field
    shipping_method = models.CharField(max_length=50, default='Standard Delivery', null=True, blank=True)
    shipping_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    total_cost = models.DecimalField(max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    # delivery_boy = models.ForeignKey(DeliveryBoy, on_delete=models.SET_NULL, null=True, blank=True)  # New field for delivery boy


    def __str__(self):
        return self.first_name

class OrderItem(models.Model):
    STATUS_CHOICES = [
        ('processing', 'Processing'),
        ('packing', 'Packing'),
        ('shipping', 'Shipping'),
        ('Out for Delivery', 'Out for Delivery'),
        ('delivered', 'Delivered'),  # Consider adding a delivered status
    ]
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, null=True, blank=True)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, null=True, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    status = models.CharField(max_length=20,choices=STATUS_CHOICES, default='processing')
    created_at=models.DateTimeField(auto_now_add=True, null=True, blank=True)

    

    def __str__(self):
        return str(self.id)

    def get_cost(self):
        return self.price * self.quantity



class Address(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True,primary_key=False,related_name='user_profile')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    address = models.CharField(max_length=255)
    zipcode = models.CharField(max_length=10)  # Add this field
    location = models.CharField(max_length=10, null=True, blank=True)  # Add this field

    def __str__(self):
        return self.first_name

class BookService(models.Model):
    STATUS_CHOICES = [
        ("pickup", "Pickup"),
        ("processing", "Processing"),
        ("parts_ordered", "Parts Ordered"),
        ("completed", "Completed"),
        ("delivered", "Delivered"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("not_paid", "Not Paid"),
        ("paid", "Paid"),
    ]

    name = models.CharField(max_length=255)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    address = models.TextField()
    location = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    issue = models.TextField()
    upload = models.FileField(upload_to="uploads/", blank=True, null=True)
    pickup_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pickup")

    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    payment_link = models.URLField(null=True, blank=True)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default="not_paid")

    def __str__(self):
        return self.name

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='profile')
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    address = models.TextField()
    location = models.CharField(max_length=100)

    def __str__(self):
        return self.user.username

# Signal to automatically create Profile when User is created
@receiver(post_save, sender=CustomUser)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

# Signal to save Profile when User is saved
@receiver(post_save, sender=CustomUser)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

class DeliveryBoy(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    username = models.CharField(max_length=100, null=True, blank=True)
    deliveryboy_name = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(unique=True, null=True, blank=True)
    area = models.CharField(max_length=50, null=True, blank=True)
    route_location = models.CharField(max_length=100, null=True, blank=True)  # New field
    password = models.CharField(max_length=50, null=True)  # Store hashed passwords instead # Not recommended to store plaintext passwords

    def __str__(self):
        return self.deliveryboy_name

class Manager(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, null=True, blank=True)
    manager_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    department = models.CharField(max_length=100)  # Manager's department
    password = models.CharField(max_length=50, null=True)  # Avoid storing passwords in plaintext

    def __str__(self):
        return self.manager_name

class Rating(models.Model):
    product = models.ForeignKey(Product, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)  # 1-5 Star Rating
    review = models.TextField(blank=True, null=True)  # Add text review
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Rating {self.rating} for {self.product.name} by {self.user.username}"

class Complaint(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("resolved", "Resolved"),
    ]
    
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    subject = models.CharField(max_length=255)
    complaint_text = models.TextField()
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="pending")
    admin_response = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Complaint by {self.user.username} - {self.subject}"


