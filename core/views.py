from django.contrib import messages
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from requests import request
from django.shortcuts import get_object_or_404, redirect
from .models import Item,OrderItem,Order,Address,Payment
from django.views.generic import ListView,DetailView,View
from django.utils import timezone
from .forms import CheckoutForm
import stripe

# stripe.api_key = "sk_test_51L2HK7SEQlo5lteprHceSIhP1lQdGiz6cK4ZMwWO7FAFOJkyYuPnIgB0v3yvBKzCnWiIV8XXOn6TjkxKTGAJOXfY00tVx05ESh"
# `source` is obtained with Stripe.js; see https://stripe.com/docs/payments/accept-a-payment-charges#web-create-token


# Create your views here.


def home(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "home.html", context)


class CheckoutView(View):
    def get(self, *args, **kwargs):
        #form
        order = Order.objects.get(user=self.request.user,ordered=False)
        form = CheckoutForm()
        context = {
            'form':form,
            'order':order
        }
        return render(self.request, "checkout.html",context)
    
    def post(self,*args,**kwargs):
            form = CheckoutForm(self.request.POST or None)

            try:
                order = Order.objects.get(user=self.request.user, ordered=False)
                if(order.items.count() == 0):
                    messages.warning(self.request,"No items are present in the cart.")
                    return redirect('/')
                print("passing through here")
                if form.is_valid():
                    print("yes it is")
                    street_address = form.cleaned_data.get('street_address')
                    apartment_address = form.cleaned_data.get('apartment_address')
                    country = form.cleaned_data.get('country')
                    zip = form.cleaned_data.get('zip')
                    payment_option = form.cleaned_data.get('payment_option')
                    address = Address(
                        user = self.request.user,
                        street_address = street_address,
                        apartment_address = apartment_address,
                        country = country,
                        zip = zip,
                    )
                    address.save()
                    order.address = address
                    order.save()

                    if payment_option == 'S':
                        return redirect("core:payment",payment_option='stripe')
                    elif payment_option=='P':
                        return redirect("core:payment",payment_option='stripe')
                    else:
                        messages.warning(self.request,"invalid payment option")
                        return redirect("core:checkout")

                messages.warning(self.request,"Failed checkout")
                return redirect("core:checkout",)
            
            except ObjectDoesNotExist:
                messages.error(self.request, "You do not have an active order")
                return redirect("/")   

       
class PaymentView(View):
    def get(self,*args,**kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order':order
        }
        return render(self.request,'payment.html',context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user,ordered=False) 
        token = self.request.POST.get('stripeToken')
        amount = int(order.get_total()*100) 

        try:
            #  uncomment the below lines to use the stripe payment gateway.
            # charge = stripe.Charge.create(
            #     amount=amount,
            #     currency="usd",
            #     source=token,
            #     description="My First Test Charge (created for API docs at https://www.stripe.com/docs/api)",
            # )

            # writing the payment 
            payment = Payment()
            payment.stripe_charge_id = "empty_id" #charge['id']
            payment.user = self.request.user
            amount = amount
            payment.save()

            # saving the final order
            order.ordered = True
            order.payment = payment
            order.save()

            messages.success(self.request,"Your order was successful")
            return redirect('/')

        except stripe.error.CardError as e:
            messages.error(self.request,"we will think about it later")
        except stripe.error.RateLimitError as e:
            messages.error(self.request,"we will think about it later")
        except stripe.error.InvalidRequestError as e:
            messages.error(self.request,"we will think about it later")
        except stripe.error.AuthenticationError as e:
            messages.error(self.request,"we will think about it later")
        except stripe.error.APIConnectionError as e:
            messages.error(self.request,"we will think about it later")
        except stripe.error.StripeError as e:
            messages.error(self.request,"we will think about it later")

        except Exception as e:
            messages.error(self.request,"hamari galti hai.")
            pass
    
       






class HomeView(ListView):
    model = Item
    paginate_by: 10
    template_name = "home.html"


def products(request):
    context = {
        'item': Item.objects.all()
    }
    return render(request, "product.html", context)


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"


class OrderSummaryView(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        try:
            order = Order.objects.get(user=self.request.user, ordered=False)
            context = {

                'object': order

            }
            return render(self.request, 'order_summary.html', context)
        except ObjectDoesNotExist:
            messages.error(self.request, "You do not have an active order")
            return redirect("/")


@login_required
def add_to_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(
                request, f"{order_item.quantity} {order_item.item.title} present in the cart now.")
        else:
            messages.info(request, f"This item was added to your cart")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(
            user=request.user, ordered_date=ordered_date)
        messages.info(request, "This item was added to your cart")
        order.items.add(order_item)

    return redirect("core:order-summary")


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = order.items.get(item__slug=item.slug)
            messages.info(request, "This item was removed from your cart")
            order.items.remove(order_item)
            order_item.delete()
            return redirect("core:order-summary")
        else:
            # adding a message that the item does not exist.
            messages.info(request, "No item exists in the cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "No item exists in the cart")
        return redirect("core:product", slug=slug)


@login_required
def remove_single_item_from_cart(request, slug):
    item = get_object_or_404(Item, slug=slug)
    order_qs = Order.objects.filter(user=request.user, ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item = order.items.filter(item__slug=item.slug)[0]
            messages.info(request, "This item quantity was updated")
            if order_item.quantity > 1:
                order_item.quantity -= 1
                order_item.save()
            else:
                order.items.remove(order_item)
            # order.items.remove(order_item)
            return redirect("core:order-summary")
        else:
            # adding a message that the item does not exist.
            messages.info(request, "No item exists in the cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request, "No item exists in the cart")
        return redirect("core:product", slug=slug)


# def cart_item_count(request):
#     count = 0
#     if(request.user.is_authenticated):
#         order_qs = Order.objects.filter(user=request.user,ordered=False)
#         if order_qs.exists():
#             order = order_qs[0]
#             count = order.items.count()
#     return count



try:
  # Use Stripe's library to make requests...
  pass
except stripe.error.CardError as e:
  # Since it's a decline, stripe.error.CardError will be caught

  print('Status is: %s' % e.http_status)
  print('Code is: %s' % e.code)
  # param is '' in this case
  print('Param is: %s' % e.param)
  print('Message is: %s' % e.user_message)
except stripe.error.RateLimitError as e:
  # Too many requests made to the API too quickly
  pass
except stripe.error.InvalidRequestError as e:
  # Invalid parameters were supplied to Stripe's API
  pass
except stripe.error.AuthenticationError as e:
  # Authentication with Stripe's API failed
  # (maybe you changed API keys recently)
  pass
except stripe.error.APIConnectionError as e:
  # Network communication with Stripe failed
  pass
except stripe.error.StripeError as e:
  # Display a very generic error to the user, and maybe send
  # yourself an email
  pass
except Exception as e:
  # Something else happened, completely unrelated to Stripe
  pass