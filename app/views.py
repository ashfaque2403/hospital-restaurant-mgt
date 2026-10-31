from django.shortcuts import render,redirect
from django.contrib import messages
from .models import Product,Cart,CartItem,CustomUser,OrderItem,Order,Category,Address,ProductImage,Brand,Profile
from django.http import HttpResponseRedirect

from django.http import JsonResponse,HttpResponse
from django.contrib.auth.decorators import login_required
from django.shortcuts import render,get_object_or_404,redirect

from django.contrib.auth import logout
from django.contrib.auth import authenticate,login
from django.contrib.auth import update_session_auth_hash

from django.http import HttpResponse
from django.core.mail import send_mail
from django.conf import settings

from django.db.models import Q
from django.http import HttpResponse
from decimal import Decimal

from django.shortcuts import render, get_object_or_404
from django.shortcuts import render
from django.http import Http404

from .models import Address, CartItem
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Order, OrderItem 
# Create your views here.
from django.shortcuts import render
from django.http import HttpResponse
from django.core.mail import send_mail, EmailMessage
from django.conf import settings


# Create your views here.
from django.shortcuts import render
from django.db.models import Q
from .models import Product, ProductImage, CartItem
@login_required
def index(request):
    products = Product.objects.all()
    product_images = ProductImage.objects.all()

    product = Product.objects.all()  
 
    cart_items = []
    total_cart_items = 0
    total_price = 0
    search = request.GET.get('search')

    if search:
        product = product.filter(Q(name__icontains=search))

    for product in products:
        product.discounted_price = product.price - (product.discount if product.discount else 0)

    # Ensure only the requested user sees their cart items
    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user)  # Fetch only the current user's cart items
        total_cart_items = cart_items.count()

        for cart_item in cart_items:
            cart_item.total_price = cart_item.product.price * cart_item.quantity
            total_price += cart_item.total_price  

    # Calculate total amount for the requested user's cart
    total_amount = total_price if cart_items else 0

    context = {
        'products': products,  
        'product_images': product_images,
        'total_amount': total_amount,
        'search': search,
        'cart_items': cart_items,  # Only requested user's cart items
        'total_cart_items': total_cart_items,
    }

    return render(request, 'index.html', context)




def logout_view(request):
    logout(request)
    return redirect(index)

def loginview(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = CustomUser.objects.filter(username=username).first()

        if not user_obj:
            messages.warning(request, 'Account not found')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        user_authenticated = authenticate(request, username=username, password=password)

        if not user_authenticated:
            messages.warning(request, 'Invalid password')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        print(f"Authenticated User: {user_authenticated}")

        login(request, user_authenticated)
        return redirect('/')

    return render(request, 'login.html')


def register(request):
    if request.method == 'POST':
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        status = request.POST.get('status')

        # Check if username or email already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'User with this Username already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'User with this email already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Create new user
        user = CustomUser.objects.create(username=username, email=email, first_name=firstname, last_name=lastname, status=status)
        user.set_password(password)
        user.save()

        return redirect('login')

    return render(request, 'register.html')


@login_required
def cart(request):
    cart_items = CartItem.objects.filter(cart__user=request.user)
    total_cart_items = 0
    total_price = 0
    total_discount = 0

    # Calculate price and discount per cart item
    for cart_item in cart_items:
        cart_item.total_price = cart_item.product.price * cart_item.quantity  # Calculate total price per item
        cart_item.total_discount = cart_item.product.discount * cart_item.quantity  # Calculate total discount per item
        
        total_price += cart_item.total_price
        total_discount += cart_item.total_discount

    discounted_amount = total_price - total_discount
    total_cart_items = cart_items.count()

    context = {
        'cart_items': cart_items,
        'total_price': total_price,
        'total_discount': total_discount,
        'total_cart_items': total_cart_items,
        'total_amount': total_price,
        'discounted_amount': discounted_amount,
    }
    return render(request, 'cart.html', context)

def checkout(request):
    try:
        address = Address.objects.get(user=request.user)
    except Address.DoesNotExist:
        address = None  # Handle case where no address exists for the user

    cart_items = CartItem.objects.filter(cart__user=request.user)
    total_price = 0
    total_discount = 0
    speed_delivery = 16
    normal_delivery = 0

    # Calculate discounts and total price
    for cart_item in cart_items:
        product_discount = cart_item.product.discount or 0  # Ensure there's a fallback if discount is None
        product_price = cart_item.product.price or 0  # Ensure there's a fallback if price is None
        cart_item.total_discount = product_discount * cart_item.quantity
        total_discount += cart_item.total_discount
        cart_item.total_price = product_price * cart_item.quantity
        total_price += cart_item.total_price

    total_carted_items = cart_items.count()
    total_amount = total_price - total_discount
    discounted_amount = total_amount
    final_amount_with_speed = discounted_amount + speed_delivery

    # Populate form data based on whether an address exists
    form_data = {
        'first_name': address.first_name if address else '',
        'last_name': address.last_name if address else '',
        'email': address.email if address else '',
        'address': address.address if address else '',
        'zipcode': address.zipcode if address else '',
    }

    context = {
        'cart_items': cart_items,
        'address': address,
        'form_data': form_data,
        'total_price': total_price,
        'total_discount': total_discount,
        'total_carted_items': total_carted_items,
        'total_amount': total_amount,
        'discounted_amount': discounted_amount,
        'final_amount_with_speed': final_amount_with_speed,
        'speed_delivery': speed_delivery,
        'normal_delivery': normal_delivery
    }
    return render(request, 'checkout.html', context)

@login_required
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart_item, created = CartItem.objects.get_or_create(cart=cart, product=product)
    cart_item.quantity += 1
    cart_item.save()
    messages.success(request, 'added to the cart')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def remove_from_cart(request,cart_item_id):
    cart_item=get_object_or_404(CartItem,id=cart_item_id)
    cart_item.delete()
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

def update_cart_item(request, item_id):
    try:
        quantity = int(request.POST.get('quantity'))
        cart_item = CartItem.objects.get(id=item_id)
        cart_item.quantity = quantity
        cart_item.total_price = cart_item.product.price * quantity  # Ensure correct price calculation
        cart_item.save()
        return JsonResponse({'status': 'success', 'message': 'Quantity updated', 'total_price': cart_item.total_price})
    except CartItem.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'Item not found'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def productpage(request, id):
    # Get the product based on the ID
    productpage = Product.objects.get(id=id)
    ratings = productpage.ratings.all()
    # Get all images for the product
    productpageimages = ProductImage.objects.filter(product=productpage)
    faqs = [
    {"question": "What is the return policy?", "answer": "You can return the product within 30 days."},
    {"question": "Does this product come with a warranty?", "answer": "Yes, it includes a 1-year warranty."},
    {"question": "How long does shipping take?", "answer": "Shipping takes 3-5 business days."},
    ]
    context = {
        "ratings": ratings,
        "faqs": faqs,
        'product': productpage,
         'productimages': productpageimages,
        }
    # Pass the product and images to the template
    return render(request, 'product_page.html',context)

from decimal import Decimal
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Cart, CartItem, Order, OrderItem

def start_order(request):
    if request.method == "POST":
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        room_no = request.POST.get('room_no')
        floor_no = request.POST.get('floor_no')

        # Fetch the cart associated with the current user
        user_cart = Cart.objects.filter(user=request.user).first()
        if not user_cart:
            messages.error(request, "No cart found for this user.")
            return redirect('cart')

        cart_items = CartItem.objects.filter(cart=user_cart)
        if not cart_items.exists():
            messages.error(request, "No items in cart.")
            return redirect('cart')

        # Calculating total price from cart items using Decimal for all arithmetic
        total_price = sum(Decimal(item.product.price) * item.quantity for item in cart_items)
        total_discount = sum(Decimal(item.product.discount) * item.quantity for item in cart_items)
        total_cost = total_price - total_discount

        # Create Order
        try:
            order = Order.objects.create(
                user=request.user,
                first_name=first_name,
                last_name=last_name,
                phone=phone,
                email=email,
                room_no=room_no,
                floor_no=floor_no,
                total_cost=total_cost
            )
            # messages.success(request, "Order created successfully!")

            # Create OrderItems and update product stock
            for item in cart_items:
                product = item.product
                if product.stock_quantity >= item.quantity:
                    order_item = OrderItem.objects.create(
                        order=order,
                        product=product,
                        price=Decimal(product.price) * item.quantity,
                        quantity=item.quantity,
                    )
                    # Update product stock quantity
                    product.stock_quantity -= item.quantity
                    product.save()
                else:
                    messages.warning(request, f"Not enough stock for product: {product.name}")
                    return redirect('cart')

            # Clear the cart
            cart_items.delete()
            # messages.success(request, "Order placed successfully!")
            return redirect('wishlist')
        except Exception as e:
            messages.error(request, f"An error occurred while placing the order: {e}")
            return redirect('cart')

    return render(request, 'cart.html')



@login_required
def wishlist(request):
    return render(request, 'payment.html')



def vworder(request):
    product_images = ProductImage.objects.all()
    
    # For buyers: List OrderItems linked to Orders made by the user
    buyer_orders = OrderItem.objects.filter(order__user=request.user).order_by('-created_at')

    # For sellers: List OrderItems linked to Products managed by the user
    seller_orders = OrderItem.objects.all().order_by('-created_at')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('action')

        if order_id:
            order = get_object_or_404(OrderItem, pk=order_id)
            if new_status in [status[0] for status in OrderItem.STATUS_CHOICES]:  # Check if new status is valid
                order.status = new_status
                order.save()
                messages.success(request, f"Order status updated to {new_status}.")
                return redirect('order')  # Make sure this matches your URL name
        else:
            messages.error(request, "Order ID not provided.")

    return render(request, 'order.html', {'buyer_orders': buyer_orders, 'seller_orders': seller_orders, 'product_images': product_images})

from django.db.models import Q

from collections import defaultdict
from django.shortcuts import render

def shop(request):
    filter_option = request.GET.get('filter', 'all')  # Get filter from URL parameters
    products = Product.objects.all()
    cart_items = CartItem.objects.all()
    category_obj = Category.objects.all()
    total_cart_items = 0

    if request.user.is_authenticated:
        cart_items = CartItem.objects.filter(cart__user=request.user)  # Fetch only the current user's cart items
        total_cart_items = cart_items.count()

    # Apply filtering
    if filter_option == "sugarless":
        products = products.filter(sugarless=True)
    elif filter_option == "saltless":
        products = products.filter(saltless=True)
    elif filter_option == "spiceless":
        products = products.filter(spiceless=True)

    # Categorize products
    categorized_products = defaultdict(list)
    for item in products:
        categorized_products[item.category.name].append(item)

    context = {
        'categorized_products': dict(categorized_products),
        'category_obj': category_obj,
        'cart_items': cart_items,
        'total_cart_items': total_cart_items,
        'filter_option': filter_option,  # Pass the current filter to the template
    }
    return render(request, 'shop.html', context)



from django.shortcuts import render, redirect




@login_required
def profile_create(request):
    # Check if the user already has a profile
    if Profile.objects.filter(user=request.user).exists():
        return redirect('profile')  # Redirect if profile already exists

    if request.method == 'POST':
        # Get the form data
        name = request.POST.get('name')
        phone_number = request.POST.get('phone_number')
        address = request.POST.get('address')
        location = request.POST.get('location')

        # Ensure no fields are empty (basic validation)
        if not all([name, phone_number, address, location]):
            return render(request, 'profile_create.html', {
                'error': 'Please fill out all fields.'
            })

        # Create and save the new profile
        profile = Profile(user=request.user, name=name, phone_number=phone_number,
                          address=address, location=location)
        profile.save()
        return redirect('profile')  # Redirect to the relevant page

    return render(request, 'profile_create.html')

@login_required
def edit_profile(request):
    profile = get_object_or_404(Profile, user=request.user)

    if request.method == 'POST':
        # Update profile fields, only if new values are provided
        profile.name = request.POST.get('name', profile.name)
        profile.phone_number = request.POST.get('phone_number', profile.phone_number)
        profile.address = request.POST.get('address', profile.address)
        profile.location = request.POST.get('location', profile.location)

        # Save the updated profile
        profile.save()
        return redirect('profile')  # Redirect to profile view after saving

    return render(request, 'edit_profile.html', {'profile': profile})


@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'profile.html', {'profile': profile})

@login_required
def address(request):
    try:
        address = Address.objects.get(user=request.user)  # Get the unique address for the user
    except Address.DoesNotExist:
        address = None  # If no address exists, set address to None

    if request.method == "POST":
        # Fetch data from form
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        address_field = request.POST.get('address')  # Avoid name conflict with 'address' variable
        zipcode = request.POST.get('zipcode')
        location = request.POST.get('location')

        if address:
            # Update existing address
            address.first_name = first_name
            address.last_name = last_name
            address.email = email
            address.address = address_field
            address.zipcode = zipcode
            address.location = location
            address.save()
            messages.success(request, 'Address updated successfully!')
        else:
            # Create new address if none exists
            Address.objects.create(user=request.user, first_name=first_name, last_name=last_name, email=email, address=address_field, zipcode=zipcode,location=location)
            messages.success(request, 'Address added successfully!')

        return redirect('address')  # Redirect to the same page to avoid resubmission of form

    # Prepare form data if address exists; otherwise, use empty strings
    form_data = {
        'first_name': address.first_name if address else '',
        'last_name': address.last_name if address else '',
        'email': address.email if address else '',
        'address': address.address if address else '',
        'zipcode': address.zipcode if address else '',
        'location': address.location if address else '',
    }

    return render(request, 'address.html', {'address': address, 'form_data': form_data})


from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Product, Category

def add_product(request):
    """View to add a product along with multiple images."""
    if request.method == "POST":
        name = request.POST.get("name")
        description = request.POST.get("description")
        price = request.POST.get("price")
        category_id = request.POST.get("category")
        discount = request.POST.get("discount", 0)
        stock_quantity = request.POST.get("stock_quantity", 0)
        images = request.FILES.get("images")  # Get multiple uploaded images

        # New fields
        sugarless = request.POST.get("sugarless") == "on"
        saltless = request.POST.get("saltless") == "on"
        spiceless = request.POST.get("spiceless") == "on"

        category = Category.objects.get(id=category_id) if category_id else None

        # Create and save the product
        product = Product.objects.create(
            name=name,
            user=request.user,
            description=description,
            price=price,
            category=category,
            discount=discount,
            stock_quantity=stock_quantity,
            image=images,
            sugarless=sugarless,
            saltless=saltless,
            spiceless=spiceless,
        )

        messages.success(request, "Product added successfully!")
        return redirect("shop")  # Redirect to the product list page

    categories = Category.objects.all()
    return render(request, "add_product.html", {"categories": categories})


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Category

@login_required
def add_category(request):
    """View to add a new category."""
    if request.method == "POST":
        name = request.POST.get("name")
        if name:
            Category.objects.create(name=name)
            messages.success(request, "Category added successfully!")
            return redirect("add_category")
        else:
            messages.error(request, "Category name cannot be empty.")

    categories = Category.objects.all()
    return render(request, "add_category.html", {"categories": categories})



@login_required
def update_product(request, product_id):
    """Update an existing product."""
    product = get_object_or_404(Product, id=product_id)

    if request.method == "POST":
        product.name = request.POST.get("name")
        product.description = request.POST.get("description")
        product.price = request.POST.get("price")
        product.discount = request.POST.get("discount")
        product.stock_quantity = request.POST.get("stock_quantity")
        images = request.FILES.get("images")

        category_id = request.POST.get("category")

        product.category = Category.objects.get(id=category_id) if category_id else None
        
        product.save()
        


        messages.success(request, "Product updated successfully!")
        return redirect("product-list")

    categories = Category.objects.all()
    return render(request, "update_product.html", {"product": product, "categories": categories})


@login_required
def delete_product(request, product_id):
    """Delete an existing product."""
    product = get_object_or_404(Product, id=product_id)
    
    if request.method == "POST":
        product.delete()
        messages.success(request, "Product deleted successfully!")
        return redirect("product-list")

    return render(request, "delete_product.html", {"product": product})


from django.shortcuts import render
from .models import Product,DeliveryBoy

def product_list(request):
    """Display a list of all products."""
    products = Product.objects.all()
    return render(request, "product_list.html", {"products": products})


@login_required
def add_deliveryboy(request):
    if request.method == "POST":
        username = request.POST.get('username')
        name = request.POST.get('name')
        email = request.POST.get('email')
        floor = request.POST.get('route_location')
        password = request.POST.get('password')

        # Check if username OR email already exists
        if CustomUser.objects.filter(username=username).exists():
            messages.warning(request, 'Username already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        if CustomUser.objects.filter(email=email).exists():
            messages.warning(request, 'Email already exists')
            return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # Create a CustomUser instance
        user_ob = CustomUser.objects.create_user(
            username=username, 
            email=email, 
            password=password, 
            is_deliveryboy=True,
            status=CustomUser.StatusChoices.DELIVERY_BOY  # Correct way to assign status
        )

        # Create a DeliveryBoy instance associated with the CustomUser
        DeliveryBoy.objects.create(
            user=user_ob,
            deliveryboy_name=name,
            email=email,
            floor=floor  # Save the floor field correctly
        )

        messages.success(request, 'DeliveryBoy added successfully')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

    return render(request, 'add_deliveryboy.html')




@login_required
def view_assigned_orders(request):
    if request.user.is_deliveryboy:
        try:
            # Fetch the DeliveryBoy profile for the logged-in user
            delivery_boy = DeliveryBoy.objects.get(user=request.user)
            # Filter orders based on the deliveryboy's route location
            assigned_orders = OrderItem.objects.filter(order__floor_no=delivery_boy.floor)

            # Handle order status update via POST
            if request.method == 'POST':
                order_id = request.POST.get('order_id')
                new_status = request.POST.get('action')

                if order_id and new_status:
                    try:
                        order_item = get_object_or_404(OrderItem, pk=order_id)
                        if new_status in [status[0] for status in OrderItem.STATUS_CHOICES]:
                            order_item.status = new_status
                            order_item.save()
                            messages.success(request, f"Order status updated to {new_status}.")
                        else:
                            messages.error(request, "Invalid status selected.")
                    except OrderItem.DoesNotExist:
                        messages.error(request, "Order item not found.")
                else:
                    messages.error(request, "Order ID or new status not provided.")
            
            # Pass assigned orders to the template
            context = {'orders': assigned_orders}
            return render(request, 'assigned_orders.html', context)

        except DeliveryBoy.DoesNotExist:
            messages.error(request, "DeliveryBoy profile not found.")
            return redirect('index')
    else:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('index')



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Complaint
from django.contrib.auth.decorators import login_required

# View to list complaints (for admins only)
@login_required
def view_complaints(request):
    if request.user.is_staff:  # Ensure only admins can view this
        complaints = Complaint.objects.all()
        return render(request, 'view_complaints.html', {'complaints': complaints})
    else:
        messages.error(request, "You are not authorized to view complaints.")
        return redirect('index')

# View to track complaint status and allow admin response
@login_required
def track_complaint(request, complaint_id):
    if request.user.is_staff:  # Ensure only admins can view and respond
        complaint = get_object_or_404(Complaint, pk=complaint_id)

        if request.method == "POST":
            status = request.POST.get('status')
            admin_response = request.POST.get('admin_response')
            
            if status in dict(Complaint.STATUS_CHOICES).keys():
                complaint.status = status
            if admin_response:
                complaint.admin_response = admin_response
                
            complaint.save()
            messages.success(request, "Complaint updated successfully.")
            return redirect('view_complaints')
        
        return render(request, 'track_complaint.html', {'complaint': complaint})
    else:
        messages.error(request, "You are not authorized to track complaints.")
        return redirect('home')

from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Complaint
from django.contrib.auth.decorators import login_required

# View to add a complaint
@login_required
def add_complaint(request):
    if request.method == "POST":
        subject = request.POST.get('subject')
        complaint_text = request.POST.get('complaint_text')

        complaint = Complaint.objects.create(
            user=request.user,
            subject=subject,
            complaint_text=complaint_text,
        )

        messages.success(request, "Your complaint has been submitted successfully.")
        return redirect('user_complaints')  # Redirect to user complaints list

    return render(request, 'add_complaint.html')

# View to list user complaints and admin responses
@login_required
def user_complaints(request):
    complaints = Complaint.objects.filter(user=request.user)  # Only fetch complaints submitted by the logged-in user
    return render(request, 'user_complaints.html', {'complaints': complaints})






























