from django.urls import path
from . import views

urlpatterns = [
    path('',views.index,name='index'),
    path('login/', views.loginview, name='login'),
    path('register/', views.register, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('cart/', views.cart, name='cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('shop/', views.shop, name='shop'),
    path('product-page/<int:id>', views.productpage, name='product-page'),

    # cart function 

    path('add/<int:id>/',views.add_to_cart,name='add'),
    path('update-cart-item/<int:item_id>/', views.update_cart_item, name='update_cart_item'),
    path('remove/<int:cart_item_id>/',views.remove_from_cart,name='remove'),
    path('start_order', views.start_order,name='start_order'),
    path('wishlist', views.wishlist,name='wishlist'),
    path('vworder', views.vworder,name="order"),

    path('profile/create/', views.profile_create, name='profile_create'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/', views.profile_view, name='profile'),
    path('address/', views.address,name="address"),
    path("add-product/", views.add_product, name="add_product"),

    path("add-category/", views.add_category, name="add_category"),
    
    path("update-product/<int:product_id>/", views.update_product, name="update-product"),
    path("delete-product/<int:product_id>/", views.delete_product, name="delete-product"),
    path("products/", views.product_list, name="product-list"),
    path('add-deliveryboy/', views.add_deliveryboy, name='add_deliveryboy'),
    path('assigned-orders/', views.view_assigned_orders, name='view_assigned_orders'),

    
    path('complaints/', views.view_complaints, name='view_complaints'),  # View all complaints
    path('complaint/<int:complaint_id>/', views.track_complaint, name='track_complaint'),
    path('add-complaint/', views.add_complaint, name='add_complaint'),  # Route for adding complaint
    path('my-complaints/', views.user_complaints, name='user_complaints'),

]