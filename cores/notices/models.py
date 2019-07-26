from django.db import models
from django.contrib.auth.models import User, Group
from enum import Enum

# Create your models here.

class NoticeStyle(Enum):
    primary = "Primary"
    secondary = "Secondary"
    success = "Success"
    danger = "Danger"
    warning = "Warning"
    info = "Info"
    light = "Light"
    dark = "Dark"

class Notice(models.Model):
    title = models.CharField(max_length=120)
    message = models.TextField(max_length=500)
    style = models.CharField(
        max_length=30,
        choices=[(tag.name, tag.value)
                 for tag in NoticeStyle],  # Choices is a list of Tuple
        null=False,
        default='info'
    )
    priority = models.IntegerField(
        choices=[
            (0, "Very High"),
            (1, "High"),
            (2, "Normal"),
            (3, "Low"),
            (4, "Very Low")
            ],  # Choices is a list of Tuple
        null=False,
        default=2
    )
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.PROTECT, null=True)
    target = models.ForeignKey(Group, on_delete=models.PROTECT, blank=True, null=True, help_text="Show only to members of this group.")
    expires = models.DateTimeField(blank=True, null=True, help_text="When should this message dissapear?")
    visible = models.BooleanField(default=True, help_text="Do you want this message to appear now?")

    def __str__(self):
        return self.title
