from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from django.views.generic import ListView, DetailView, View
from django.shortcuts import render, get_object_or_404
from .forms import CheckoutForm
from .models import Product, Category, SubCategory, Review, Order, OrderItem, ShippingAddress
from .forms import ReviewForm


def products(request):
    context = {
        'products': Product.objects.all()
    }
    return render(request, "products.html", context)


def is_valid_form(values):
    valid = True
    for field in values:
        if field == '':
            valid = False
    return valid


def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'signup.html', {'form': form})


class CheckoutView(View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            form = CheckoutForm()
            context = {
                'form': form,
                'order': order,
            }

            shipping_address_qs = ShippingAddress.objects.filter(
                user=self.request.user,
                default=True
            )
            if shipping_address_qs.exists():
                context.update(
                    {'default_shipping_address': shipping_address_qs[0]})

            return render(self.request, "checkout.html", context)

        except ObjectDoesNotExist:
            messages.info(self.request, "You do not have an active order")
            return redirect("core:checkout")

    def post(self, *args, **kwargs):
        form = CheckoutForm(self.request.POST or None)
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            if form.is_valid():

                use_default_shipping = form.cleaned_data.get(
                    'use_default_shipping')
                if use_default_shipping:
                    print("Using the defualt shipping address")
                    address_qs = ShippingAddress.objects.filter(
                        user=self.request.user,
                        default=True
                    )
                    if address_qs.exists():
                        shipping_address = address_qs[0]
                        order.shipping_address = shipping_address
                        order.save()
                    else:
                        messages.info(
                            self.request, "No default shipping address available")
                        return redirect('core:checkout')
                else:
                    print("User is entering a new shipping address")
                    shipping_address1 = form.cleaned_data.get(
                        'shipping_address')
                    shipping_address2 = form.cleaned_data.get(
                        'shipping_address2')
                    shipping_country = form.cleaned_data.get(
                        'shipping_country')
                    shipping_zip = form.cleaned_data.get('shipping_zip')

                    if is_valid_form([shipping_address1, shipping_country, shipping_zip]):
                        shipping_address = ShippingAddress(
                            user=self.request.user,
                            street_address=shipping_address1,
                            apartment_address=shipping_address2,
                            country=shipping_country,
                            zip=shipping_zip,
                        )
                        shipping_address.save()

                        order.shipping_address = shipping_address
                        order.save()

                        set_default_shipping = form.cleaned_data.get(
                            'set_default_shipping')
                        if set_default_shipping:
                            shipping_address.default = True
                            shipping_address.save()

                    else:
                        messages.info(
                            self.request, "Please fill in the required shipping address fields")

                payment_option = form.cleaned_data.get('payment_option')

                if payment_option == 'S':
                    return redirect('core:payment', payment_option='stripe')
                elif payment_option == 'P':
                    return redirect('core:payment', payment_option='paypal')
                else:
                    messages.warning(
                        self.request, "Invalid payment option selected")
                    return redirect('core:checkout')
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("core:order-summary")


class HomeView(ListView):
    model = Product
    paginate_by = 10
    template_name = "home.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        categories = Category.objects.all()
        favorite_products = Product.objects.filter(rating__gte=4)
        context['categories'] = categories
        context['favorite_products'] = favorite_products
        return context


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {
                'object': order
            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.warning(self.request, "You do not have an active order")
            return redirect("/")


class ItemDetailView(DetailView):
    model = Product
    template_name = "product.html"


@login_required
def add_to_cart(request, id):
    product = get_object_or_404(Product, id=id)
    order_item, created = OrderItem.objects.get_or_create(
        product=product,
        user=request.user,
        ordered=False
    )
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.products.filter(product__id=product.id).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            order.products.add(order_item)
            messages.info(request, "This item was added to your cart.")
            return redirect("core:order-summary")
    else:
        order = Order.objects.create(user=request.user)
        order.products.add(order_item)
        messages.info(request, "This item was added to your cart.")
        return redirect("core:order-summary")


@login_required
def remove_from_cart(request, id):
    product = get_object_or_404(Product, id=id)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.products.filter(product__id=product.id).exists():
            order_item = OrderItem.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            order.products.remove(order_item)
            order_item.delete()
            messages.info(request, "This item was removed from your cart.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product_detail", product_id=id)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product_detail", product_id=id)


@login_required
def remove_single_item_from_cart(request, id):
    product = get_object_or_404(Product, id=id)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.products.filter(product__id=product.id).exists():
            order_item = OrderItem.objects.filter(
                product=product,
                user=request.user,
                ordered=False
            )[0]
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.products.remove(order_item)
            messages.info(request, "This item quantity was updated.")
            return redirect("core:order-summary")
        else:
            messages.info(request, "This item was not in your cart")
            return redirect("core:product_detail", product_id=id)
    else:
        messages.info(request, "You do not have an active order")
        return redirect("core:product_detail", product_id=id)


class CategoryView(View):
    def get(self, *args, **kwargs):
        category = Category.objects.get(id=self.kwargs['id'])
        product = Product.objects.filter(category=category, is_active=True)
        context = {
            'object_list': product,
            'category_title': category,
        }
        return render(self.request, "category.html", context)


class SubCategoryView(View):
    def get(self, *args, **kwargs):
        subcategory = SubCategory.objects.get(title=self.kwargs['title'])
        item = Product.objects.filter(subcategory=subcategory, is_active=True)
        context = {
            'object_list': item,
            'subcategory_title': subcategory,
        }
        return render(self.request, "subcategory.html", context)


def category_list(request):
    categories = Category.objects.all()
    context = {'categories': categories}
    return render(request, 'base.html', context)


def category(request, name):
    category = get_object_or_404(Category, name=name)
    products = Product.objects.filter(category=category)
    all_products = Product.objects.all
    categories = Category.objects.all()
    subcategories = SubCategory.objects.all
    context = {'category': category, 'products': products, 'categories': categories,
               'subcategories': subcategories, 'all_products': all_products}
    return render(request, 'category.html', context)


def product_detail(request, product_id):
    # Retrieve the product with the specified ID from the database
    product = get_object_or_404(Product, id=product_id)
    category_name = product.category.name
    categories = Category.objects.all()

    # Get related products (for example, products in the same category)
    related_products = Product.objects.filter(
        category=product.category).exclude(id=product.id)[:4]

    # Calculate the average rating for the product
    reviews = product.numReviews

    if reviews > 0:
        avg_rating = sum([review.rating for review in reviews]) / reviews
        avg_rating = round(avg_rating, 1)
    else:
        avg_rating = None

    # Instantiate the ReviewForm instance and pass it to the template context
    form = ReviewForm()

    # Render the template with the product details and the review form
    return render(request, 'product_detail.html', {
        'product': product,
        'related_products': related_products,
        'num_reviews': reviews,
        'avg_rating': avg_rating,
        'category_name': category_name,
        'form': form,
        'categories': categories
    })


@login_required
def add_review(request, pk):
    product = get_object_or_404(Product, pk=pk)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.product = product
            review.user = request.user
            review.save()
            messages.success(
                request, 'Your review has been added successfully!')
            return redirect('product', pk=pk)
    else:
        form = ReviewForm()
    return render(request, 'add_review.html', {'form': form, 'product': product})


@login_required
def edit_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        return redirect('home')
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            messages.success(
                request, 'Your review has been updated successfully!')
            return redirect('product', pk=review.product.pk)
    else:
        form = ReviewForm(instance=review)
    return render(request, 'edit_review.html', {'form': form, 'review': review})


@login_required
def delete_review(request, pk):
    review = get_object_or_404(Review, pk=pk)
    if review.user != request.user:
        return redirect('home')
    product_pk = review.product.pk
    review.delete()
    messages.success(request, 'Your review has been deleted successfully!')
    return redirect('product', pk=product_pk)
