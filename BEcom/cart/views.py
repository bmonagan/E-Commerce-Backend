from django.shortcuts import render, redirect
from .models import Product, CartItem
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from .models import Order
def product_list(request):
    products = Product.objects.all()
    return render(request, 'cart/product_list.html', {'products': products})

def view_cart(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to view your cart.')
        return redirect(f"{reverse('login')}?next={request.path}")
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def add_to_cart(request, product_id):
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to add items to your cart.")
        return redirect(f"{reverse('login')}?next={request.path}")
    product = Product.objects.get(id=product_id)
    cart_item, created = CartItem.objects.get_or_create(product=product, 
                                                       user=request.user)
    cart_item.quantity += 1
    cart_item.save()
    return redirect('cart:view_cart')

def remove_from_cart(request, item_id):
    cart_item = CartItem.objects.get(id=item_id)
    cart_item.delete()
    return redirect('cart:view_cart')


def home(request):
    return render(request, 'cart/home.html')

def checkout(request):
    if not request.user.is_authenticated:
        messages.error(request, 'You need to be logged in to checkout.')
        return redirect(f"{reverse('login')}?next={request.path}")
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart/checkout.html', {'cart_items': cart_items, 'total_price': total_price})




def clear_user_cart_session(request):
    if request.user.is_authenticated:
        CartItem.objects.filter(user=request.user).delete()
        print(f"Session cart cleared for user: {request.user.username}")
        return HttpResponseRedirect('/cart/cart')
    else:
        messages.error(request, 'You need to be logged in to clear your cart.')
        return redirect(f"{reverse('login')}?next={request.path}")


@login_required
def order_history(request):
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'cart/order_history.html', {'orders': orders})


