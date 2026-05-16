from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Order, UserStats
from decimal import Decimal

@receiver(post_save, sender=Order)
def update_user_stats_on_order_save(sender, instance, created, **kwargs):
    """
    Update UserStats whenever an Order is saved.
    """
    if created: # We only want to run this when an order is first created.
        user = instance.user
        # Get or create the stats object for the user.
        stats, _ = UserStats.objects.get_or_create(user=user)

        # Update the stats.
        stats.order_count += 1
        stats.total_spent += Decimal(str(instance.total))
        stats.save()
