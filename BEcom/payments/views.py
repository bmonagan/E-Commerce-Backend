from django.views.generic.base import TemplateView
from django.shortcuts import render
from django.urls import path
from django.conf import settings 
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt 
import stripe 

def checkout(request):
    return render(request, 'payments/checkout.html')
def SuccessView(request):
    return render(request, 'payments/success.html')
def CancelledView(request):
    return render(request, 'payments/cancelled.html')



#crsf exempt is used to exempt the view from CSRF verification
# This is useful for API endpoints that are not protected by CSRF tokens
@csrf_exempt
def stripe_config(request):
    if request.method == 'GET':
        stripe_config = {'publicKey': settings.STRIPE_PUBLISHABLE_KEY}
        return JsonResponse(stripe_config, safe=False)


from cart.models import CartItem  # Import your CartItem model

@csrf_exempt
def create_checkout_session(request):
    if request.method == 'GET':
        if not request.user.is_authenticated:
            return JsonResponse({'error': 'User not authenticated'}, status=403)
        domain_url = 'http://localhost:8000/'
        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            # Get cart items for the current user
            cart_items = CartItem.objects.filter(user=request.user)
            if not cart_items.exists():
                return JsonResponse({'error': 'Cart is empty'}, status=400)

            # Build Stripe line_items from cart
            line_items = []
            for item in cart_items:
                line_items.append({
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': item.product.name,
                        },
                        'unit_amount': int(item.product.price * 100),  # Stripe expects amount in cents
                    },
                    'quantity': item.quantity,
                })

            checkout_session = stripe.checkout.Session.create(
                success_url=domain_url + 'checkout/success?session_id={CHECKOUT_SESSION_ID}',
                cancel_url=domain_url + 'checkout/cancelled/',
                payment_method_types=['card'],
                mode='payment',
                line_items=line_items,
                metadata={
                    'user_id': request.user.id,
                    'cart_items': ','.join([str(item.id) for item in cart_items])
                }
            )
            return JsonResponse({'sessionId': checkout_session['id']})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

@csrf_exempt
def stripe_webhook(request):
    stripe.api_key = settings.STRIPE_SECRET_KEY
    endpoint_secret = settings.STRIPE_ENDPOINT_SECRET
    payload = request.body
    sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError as e:
        # Invalid payload
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return HttpResponse(status=400)

    # Handle the checkout.session.completed event
    if event['type'] == 'checkout.session.completed':
        print("Payment was successful.")
        # TODO: run some custom code here

    return HttpResponse(status=200)