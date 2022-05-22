from django.contrib import messages
from django.shortcuts import render
from .models import Item,OrderItem,Order
from django.views.generic import ListView,DetailView
from django.utils import timezone
from django.shortcuts import get_object_or_404,redirect

# Create your views here.


def home(request):
    context = {
        'items': Item.objects.all()
    }
    return render(request, "home.html", context)


def checkout(request):
    context = {}
    return render(request, "checkout.html", context)


class HomeView(ListView):
    model=Item
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


def add_to_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_item,created = OrderItem.objects.get_or_create(
        item=item,
        user=request.user,
        ordered=False)
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug=item.slug).exists():
            order_item.quantity += 1
            order_item.save()
            messages.info(request,f"{order_item.quantity} {order_item.item.title} present in the cart now.")
        else:
            messages.info(request,f"This item was added to your cart")
            order.items.add(order_item)
    else:
        ordered_date = timezone.now()
        order = Order.objects.create(user = request.user,ordered_date=ordered_date)
        messages.info(request,"This item was added to your cart")
        order.items.add(order_item)
    
    return redirect("core:product",slug=slug)

def remove_from_cart(request,slug):
    item = get_object_or_404(Item,slug=slug)
    order_qs = Order.objects.filter(user=request.user,ordered=False)
    if order_qs.exists():
        order = order_qs[0]
        if order.items.filter(item__slug = item.slug).exists():
            order_item = order.items.filter(item__slug=item.slug)[0]
            messages.info(request,"This item was removed from your cart")
            order_item.quantity = 1
            order_item.save()
            order.items.remove(order_item)
            return redirect("core:product",slug=slug)
        else:
            # adding a message that the item does not exist.
            messages.info(request,"No item exists in the cart")
            return redirect("core:product", slug=slug)
    else:
        messages.info(request,"No item exists in the cart")
        return redirect("core:product", slug=slug)
    

# def cart_item_count(request):
#     count = 0
#     if(request.user.is_authenticated):
#         order_qs = Order.objects.filter(user=request.user,ordered=False)
#         if order_qs.exists():
#             order = order_qs[0]
#             count = order.items.count()
#     return count

