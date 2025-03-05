from django.db import models

class BaseModel(models.Model):
    """
    Abstract base model that includes common fields for other models.

    Attributes:
        created_date (datetime): Timestamp for when the object was created. Automatically set when the object is created.
        updated_date (datetime): Timestamp for when the object was last updated. Automatically set when the object is updated.
        is_active (bool): Indicates whether the object is currently active. Indicates if the object is active.
    """
    created_date = models.DateTimeField(auto_now_add=True)
    updated_date = models.DateTimeField(auto_now=True, null=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True