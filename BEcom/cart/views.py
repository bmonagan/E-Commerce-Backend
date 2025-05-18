from django.shortcuts import render, redirect
from .models import Product, CartItem
from django.http import HttpResponse

def product_list(request):
    products = Product.objects.all()
    return render(request, 'cart/product_list.html', {'products': products})

def view_cart(request):
    if not request.user.is_authenticated:
        return render(request, 'cart/cart.html', {'cart_items': [], 'total_price': 0})
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart/cart.html', {'cart_items': cart_items, 'total_price': total_price})

def add_to_cart(request, product_id):
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
        return redirect('cart:view_cart')
    cart_items = CartItem.objects.filter(user=request.user)
    total_price = sum(item.product.price * item.quantity for item in cart_items)
    return render(request, 'cart/checkout.html', {'cart_items': cart_items, 'total_price': total_price})