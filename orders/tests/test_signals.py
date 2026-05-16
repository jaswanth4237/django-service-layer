from django.test import TestCase
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from orders.models import Order, UserStats
import orders.signals # This registers the signal!

class SignalTests(TestCase):
    def setUp(self):
        # Ensure the signal is connected for these tests, just in case
        post_save.connect(orders.signals.update_user_stats_on_order_save, sender=Order)

    def tearDown(self):
        # Disconnect to isolate test!
        post_save.disconnect(orders.signals.update_user_stats_on_order_save, sender=Order)

    def test_bulk_update_bypasses_signal(self):
        user1 = User.objects.create_user('user1', 'u1@test.com', 'pwd')
        user2 = User.objects.create_user('user2', 'u2@test.com', 'pwd')

        # Create two orders for user1 to initialize stats
        Order.objects.create(user=user1, total=10.0)
        Order.objects.create(user=user1, total=20.0)

        stats1 = UserStats.objects.get(user=user1)
        self.assertEqual(stats1.order_count, 2)
        self.assertEqual(float(stats1.total_spent), 30.0)

        # Create orders for user2 using bulk_create (also bypasses signal)
        orders_to_create = [
            Order(user=user2, total=15.0),
            Order(user=user2, total=25.0)
        ]
        Order.objects.bulk_create(orders_to_create)

        # Now, use update() to change the user to user1
        Order.objects.filter(user=user2).update(user=user1)

        # Fetch stats1 again
        stats1.refresh_from_db()

        # The stats should not have changed, proving update() bypasses the signal
        self.assertEqual(stats1.order_count, 2)
        self.assertEqual(float(stats1.total_spent), 30.0)
