from django_cron import CronJobBase, Schedule
from django.utils import timezone

from seller.models import Order
from .utils import get_basket_expire_date


class DeleteExpiredBasketsCronJob(CronJobBase):
    schedule = Schedule(run_every_mins=1)
    code = 'store.check_and_delete_if_basket_expired'

    def do(self):
        for preorder in Order.objects.filter(status=Order.Status.PREORDER):
            if get_basket_expire_date(preorder) < \
                    timezone.make_naive(timezone.now()):
                preorder.delete()
