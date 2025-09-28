from __future__ import annotations

from tortoise import fields
from tortoise.models import Model


class NameRequest(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        "models.User",
        related_name="name_requests",
        on_delete=fields.CASCADE,
    )
    input_name = fields.CharField(max_length=255)
    katakana = fields.CharField(max_length=255)
    romaji = fields.CharField(max_length=255)
    provider = fields.CharField(max_length=50)
    delivered = fields.BooleanField(default=False)
    delivered_at = fields.DatetimeField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "name_requests"
