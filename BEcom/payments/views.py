from django.shortcuts import render, redirect 
from django.urls import reverse 
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages 
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator

import stripe
from stripe import StripeError
from django.views import View
from django.views.generic import TemplateView



from cart.models import CartItem, Order, OrderItem
from payments.models import UserPayment
from cart.views import clear_user_cart_session

def SuccessView(request):
    clear_user_cart_session(request)
    return render(request, 'payments/success.html')
def CancelledView(request):
    return render(request, 'payments/cancelled.html')



def checkout(request): 
    if not request.user.is_authenticated:
        messages.error(request, "You must be logged in to proceed to checkout.")
        return redirect(f"{reverse('login')}?next={request.path}")
    stripe.api_key = settings.STRIPE_SECRET_KEY

    try:
        # Get cart items for the current user
        cart_items = CartItem.objects.filter(user=request.user)
        if not cart_items.exists():
            messages.info(request, "Your cart is empty.")
            return redirect(reverse('cart:view_cart'))

        line_items = []
        for item in cart_items:
            # Basic validation for product details
            if not all([item.product, item.product.name, item.product.price is not None]):
                messages.error(request, f"Missing details for a product in your cart. Please review your cart.")
                #log the problematic item for debugging
                print(f"Problematic cart item ID: {item.product}")
                return redirect(reverse('cart:view_cart')) 
            
            line_items.append({
                'price_data': {
                    'currency': 'usd',
                    'product_data': {
                        'name': item.product.name,
                        'images': [request.build_absolute_uri(item.product.image.url)] if item.product.image else [],
                        'description': item.product.description if item.product.description else '',
                        
                        
                    },
                    'unit_amount': int(item.product.price * 100),  # Stripe expects amount in cents
                },
                'quantity': item.quantity,
            })
        
        if not line_items: 
            messages.info(request, "No items eligible for checkout.")
            return redirect(reverse('cart:view_cart'))


        # Dynamically build success and cancel URLs
        success_url = request.build_absolute_uri(
            reverse('payments:success') + '?session_id={CHECKOUT_SESSION_ID}'
        )
        cancel_url = request.build_absolute_uri(
            reverse('payments:cancelled')
        )

        checkout_session_params = {
            'success_url': success_url,
            'cancel_url': cancel_url,
            'payment_method_types': ['card'],
            'mode': 'payment',
            'line_items': line_items,
            'metadata': {
                'user_id': request.user.id,
               }
        }
        
        # Create a checkout session
        checkout_session = stripe.checkout.Session.create(**checkout_session_params)
        
        # Redirect to Stripe's checkout page
        return redirect(checkout_session.url, status=303) # 303 See Other is appropriate

    except StripeError as e:
        # Handle Stripe API errors
        messages.error(request, f"Stripe error: {str(e)}")
        print(f"Stripe error: {str(e)}") # Log the error
        return redirect(reverse('cart:view_cart')) # could also be a generic error page
    except Exception as e:
        # Handle other unexpected errors
        messages.error(request, f"An unexpected error occurred. Please try again.")
        print(f"Unexpected error during checkout: {str(e)}") # Log the error
        return redirect(reverse('cart:view_cart')) 


def create_order_for_user(user):
    cart_items = CartItem.objects.filter(user=user)
    order = Order.objects.create(
        user=user,
        total=sum(item.product.price * item.quantity for item in cart_items),
        status='paid'
    )
    for item in cart_items:
        OrderItem.objects.create(
            order=order,
            product=item.product,
            quantity=item.quantity,
            price=item.product.price
        )
    cart_items.delete()  # Clear cart after order
    return order


@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config_data = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config_data, safe=False)

@csrf_exempt
def create_checkout_session(request): # This view returns JSON for client-side JS handling
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=403)
        
        # Using request.build_absolute_uri('/') for a more dynamic domain base
        domain_base_url = request.build_absolute_uri('/')
        stripe.api_key = settings.STRIPE_SECRET_KEY
        
        try:
            cart_items = CartItem.objects.filter(user=request.user)
            if not cart_items.exists():
                return JsonResponse({'error': 'Cart is empty'}, status=400)

            line_items = []
            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {'name': item.product.name,},
                        'unit_amount': int(item.product.price * 100),
                    },
                    'quantity': item.quantity,
                })

            # Using reverse for success/cancel URLs is more robust
            success_url_path = reverse('payments:success') + '?session_id={CHECKOUT_SESSION_ID}'
            cancel_url_path = reverse('payments:cancelled')

            checkout_session = stripe.checkout.Session.create(
                success_url=domain_base_url.rstrip('/') + success_url_path,
                cancel_url=domain_base_url.rstrip('/') + cancel_url_path,
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                metadata={
                    'user_id': request.user.id,
                }
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@require_POST
@csrf_exempt
def stripe_webhook(request):
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
    payload = request.body
    signature_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None
    
    try:
        event = stripe.Webhook.construct_event(
            payload, signature_header, endpoint_secret
        )
    except:
        return HttpResponse(status=400)
    
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']
        user_id = session['metadata'].get('user_id')
        # Only create the order if user_id is present
        if user_id:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id)
                create_order_for_user(user)  
            except User.DoesNotExist:
                pass  # Optionally log this
    
    return HttpResponse(status=200)