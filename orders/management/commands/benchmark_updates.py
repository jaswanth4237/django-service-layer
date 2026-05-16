from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.db.models import F
from django.db.models.signals import post_save
from orders.models import Order, UserStats
import orders.signals
import time

class Command(BaseCommand):
    help = 'Benchmarks the performance of the signal vs. service layer approaches'

    def handle(self, *args, **options):
        # 1. Signal Simulation
        user1 = User.objects.create_user('bench_user1', 'b1@test.com', 'pwd')
        
        # Connect signal just for this benchmark
        post_save.connect(orders.signals.update_user_stats_on_order_save, sender=Order)
        
        start_time_signal = time.time()
        for i in range(1000):
            Order.objects.create(user=user1, total=10.0)
        end_time_signal = time.time()
        signal_duration = end_time_signal - start_time_signal

        # Disconnect signal
        post_save.disconnect(orders.signals.update_user_stats_on_order_save, sender=Order)

        # 2. Optimized Service Simulation
        user2 = User.objects.create_user('bench_user2', 'b2@test.com', 'pwd')

        start_time_service = time.time()
        orders_to_create = [Order(user=user2, total=10.0) for _ in range(1000)]
        Order.objects.bulk_create(orders_to_create)
        
        total_spent = sum([order.total for order in orders_to_create])
        count = len(orders_to_create)

        stats, created = UserStats.objects.get_or_create(user=user2)
        UserStats.objects.filter(id=stats.id).update(
            order_count=F('order_count') + count,
            total_spent=F('total_spent') + total_spent
        )
        end_time_service = time.time()
        service_duration = end_time_service - start_time_service

        speedup = signal_duration / service_duration if service_duration > 0 else float('inf')

        self.stdout.write(f"Signal approach time: {signal_duration:.4f}s")
        self.stdout.write(f"Optimized service time: {service_duration:.4f}s")
        self.stdout.write(f"Speedup factor: {speedup:.2f}x")
