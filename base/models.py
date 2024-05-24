from django.db import models

# Base Model
class BaseModel(models.Model):
    """
    Abstract base model representing common fields for other models.

    This abstract base model provides common fields like 'created_at' and 'updated_at'
    for other models to inherit. It automatically timestamps the creation and last
    update times of model instances.

    Attributes:
        created_at (DateTimeField): A datetime field representing the creation date
            of the model instance. It's set to the current datetime when the instance
            is first created.
        updated_at (DateTimeField): A datetime field representing the last update date
            of the model instance. It's updated automatically to the current datetime
            whenever the instance is modified.

    Meta:
        abstract (bool): Specifies that this model is abstract and should not create
            its own database table. Other models can inherit from it to reuse its fields.
    """
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Updated Date")

    class Meta:
        abstract = True