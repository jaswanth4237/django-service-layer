from django.test import TestCase
from django.contrib.auth.models import User
from orders.models import Order, UserStats
from orders import services

from django.db.models.signals import post_save
import orders.signals

class ServiceTests(TestCase):
    def setUp(self):
        post_save.disconnect(orders.signals.update_user_stats_on_order_save, sender=Order)

    def test_create_order_service(self):
        user = User.objects.create_user('user1', 'u1@test.com', 'pwd')
        order = services.create_order(user, 100.50)

        self.assertIsInstance(order, Order)
        
        stats = UserStats.objects.get(user=user)
        self.assertEqual(stats.order_count, 1)
        self.assertEqual(float(stats.total_spent), 100.50)
