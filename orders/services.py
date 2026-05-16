from django.db import transaction
from django.contrib.auth.models import User
from .models import Order, UserStats
from decimal import Decimal

def create_order(user: User, total: float) -> Order:
    """
    Creates an order and updates user statistics within a single database transaction.
    """
    with transaction.atomic():
        order = Order.objects.create(user=user, total=total)

        stats, _ = UserStats.objects.get_or_create(user=user)
        stats.order_count += 1
        stats.total_spent += Decimal(str(order.total))
        stats.save()

    return order
