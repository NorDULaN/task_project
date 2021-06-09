from django.apps import AppConfig
from django.utils.translation import pgettext_lazy


class OrderAppConfig(AppConfig):
    name = 'task.order'

class OrderStatus:
    OPEN = 'open'
    CLOSED = 'closed'
    CANCELED = 'canceled'
    HOLD = 'on hold'
    SHIPPED = 'shipped'
    TEST = 'test'
    ALL = 'all'
    ALL_MINUS_TEST = 'all_minus_test'
    PRE_ORDER = 'pre order'
    ONE_CLICK = 'one click'
    NO_ANSWER = 'no answer'
    SEND_TO_DEALER = 'send to dealer'
    CALL_BACK_REQUEST = 'call back request'

    CHOICES = [
        (OPEN, pgettext_lazy('order status', 'Open')),
        (CLOSED, pgettext_lazy('order status', 'Closed')),
        (CANCELED, pgettext_lazy('order status', 'Canceled')),
        (HOLD, pgettext_lazy('order status', 'On hold')),
        (SHIPPED, pgettext_lazy('order status', 'Shipped')),
        (TEST, pgettext_lazy('order status', 'Test')),
        (PRE_ORDER, pgettext_lazy('order status', 'Pre-order')),
        (ONE_CLICK, pgettext_lazy('order status', 'One click')),
        (NO_ANSWER, pgettext_lazy('no answer', 'No answer')),
        (SEND_TO_DEALER, pgettext_lazy('send to dealer', 'Send to dealer')),
        (NO_ANSWER, pgettext_lazy('no answer', 'No answer')),
        (CALL_BACK_REQUEST, pgettext_lazy('call back request', 'Call Back Request'))
    ]

    FILTER_CHOICES = [
        (ALL, pgettext_lazy('order status', 'All')),
        (OPEN, pgettext_lazy('order status', 'Open')),
        (CLOSED, pgettext_lazy('order status', 'Closed')),
        (CANCELED, pgettext_lazy('order status', 'Canceled')),
        (HOLD, pgettext_lazy('order status', 'On hold')),
        (SHIPPED, pgettext_lazy('order status', 'Shipped')),
        (TEST, pgettext_lazy('order status', 'Test')),
        (PRE_ORDER, pgettext_lazy('order status', 'Pre-order')),
        (ONE_CLICK, pgettext_lazy('order status', 'One click')),
        (NO_ANSWER, pgettext_lazy('no answer', 'No answer')),
        (SEND_TO_DEALER, pgettext_lazy('send to dealer', 'Send to dealer')),
        (NO_ANSWER, pgettext_lazy('no answer', 'No answer')),
        (CALL_BACK_REQUEST, pgettext_lazy('call back request', 'Call Back Request'))
    ]


class GroupStatus:
    NEW = 'new'
    CANCELLED = 'cancelled'
    SHIPPED = 'shipped'

    CHOICES = [
        (NEW, pgettext_lazy('group status', 'Processing')),
        (CANCELLED, pgettext_lazy('group status', 'Cancelled')),
        (SHIPPED, pgettext_lazy('group status', 'Shipped'))]


class OrderType:
    PRE_ORDER = 'pre-order'
    ONE_CLICK = 'one click order'
    TYPICAL = 'typical'

    CHOICES = [
        (PRE_ORDER, pgettext_lazy('order type', 'pre-order')),
        (ONE_CLICK, pgettext_lazy('order type', 'one click order')),
        (TYPICAL, pgettext_lazy('order type', 'typical'))
    ]

    ORDER_STATUS_ALIAS = {
        PRE_ORDER: [OrderStatus.PRE_ORDER],
        ONE_CLICK: [OrderStatus.ONE_CLICK],
        TYPICAL: [OrderStatus.OPEN, OrderStatus.CLOSED, OrderStatus.CANCELED, OrderStatus.HOLD, OrderStatus.SHIPPED,
                  OrderStatus.TEST, OrderStatus.ALL]
    }
