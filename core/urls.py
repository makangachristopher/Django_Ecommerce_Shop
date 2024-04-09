from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .views import (
    ItemDetailView,
    CheckoutView,
    HomeView,
    OrderSummaryView,
    add_to_cart,
    remove_from_cart,
    remove_single_item_from_cart,
    CategoryView,
    SubCategoryView,
    category_list,
    products,
    product_detail,
    signup,
    category,
    edit_review,
    add_review,
    delete_review
)

app_name = 'core'

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('signup/', signup, name='signup'),
    path('order-summary/', OrderSummaryView.as_view(), name='order-summary'),
    path('products/<int:pk>/', products, name='products'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
    path('category_details/<str:name>/', category, name='category_details'),
    path('category/<str:name>/', category, name='category'),
    path('categories', category_list, name='categories'),
    path('subcategory/<title>/', SubCategoryView.as_view(), name='subcategory'),
    path('add-to-cart/<int:id>', add_to_cart, name='add-to-cart'),
    path('remove-from-cart/<int:id>/', remove_from_cart, name='remove-from-cart'),
    path('remove-item-from-cart/<int:id>/', remove_single_item_from_cart,
         name='remove-single-item-from-cart'),
    path('product/<int:id>/add_review/', add_review, name='add_review'),
    path('review/<int:id>/edit/', edit_review, name='edit_review'),
    path('review/<int:id>/delete/',delete_review, name='delete_review')
    # path('payment/<payment_option>/', PaymentView.as_view(), name='payment'),
    # path('request-refund/', RequestRefundView.as_view(), name='request-refund')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

