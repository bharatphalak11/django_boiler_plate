from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet


class CustomModelViewSet(mixins.CreateModelMixin,
                         mixins.RetrieveModelMixin,
                         mixins.UpdateModelMixin,
                         mixins.DestroyModelMixin,
                         mixins.ListModelMixin,
                         GenericViewSet):
    """
    A viewset that provides default `create()`, `retrieve()`, `update()`,
    `partial_update()`, `destroy()` and `list()` actions.
    """
    pass

class CustomReadOnlyModelViewSet(mixins.RetrieveModelMixin,
                                 mixins.ListModelMixin,
                                 GenericViewSet):
    """
    A viewset that provides default `retrieve()`, and `list()` actions.
    """
    pass