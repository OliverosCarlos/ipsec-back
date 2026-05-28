import uuid

from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models

from entities.models.employees import Employee


class BaseModel(models.Model):
    """Clase base abstracta para campos comunes de auditoría."""

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        abstract = True


class Comment(models.Model):
    content = models.TextField()
    employee = models.ForeignKey(
        Employee, on_delete=models.CASCADE, blank=True, null=True
    )
    event = models.CharField(max_length=250)
    comment_type = models.CharField(max_length=250)
    log_type = models.CharField(max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    data = models.CharField(max_length=250, blank=True, null=True)

    # Polimorfismo usado para relacionar comentarios con varios modelos
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.CharField(max_length=36)
    related_object = GenericForeignKey("content_type", "object_id")

    class Meta:
        verbose_name = "Cometario"
        verbose_name_plural = "Comentarios"


class CommentAttachment(models.Model):
    comment = models.ForeignKey(
        Comment, related_name="attachments", on_delete=models.CASCADE
    )
    file = models.FileField(upload_to="comment_files/%Y/%m/%d/")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def filename(self):
        return self.file.name.split("/")[-1]

    def __str__(self):
        return f"{self.comment.id} - {self.filename()}"


class EntityModel(models.Model):
    """
    Describe una entidad del frontend (partner, department, product, etc.).
    Refleja la interface `EntityModel` usada en Atomic Angular.
    """

    code = models.SlugField(
        max_length=60,
        unique=True,
        help_text="Identificador estable (ej: 'partner', 'department').",
    )
    name = models.CharField(max_length=120)
    plural_name = models.CharField(max_length=120)
    model = models.CharField(
        max_length=120,
        blank=True,
        default="",
        help_text="Alias del modelo backend (ej: 'partner').",
    )
    is_active = models.BooleanField(default=True)

    views = models.JSONField(blank=True, default=list)
    search_attributes = models.JSONField(blank=True, default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "core_entity_model"
        ordering = ["code"]
        verbose_name = "Entity Model"
        verbose_name_plural = "Entity Models"

    def __str__(self) -> str:
        return f"{self.code} ({self.name})"