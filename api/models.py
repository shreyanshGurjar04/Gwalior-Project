from django.db import models
from django.utils import timezone


class Batch(models.Model):
    name = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    date = models.DateTimeField(null=True, blank=True)
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    batch_size = models.IntegerField(null=True, blank=True)
    breakout_samples = models.IntegerField(null=True, blank=True)
    batch_status = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Batch"


class Inventory(models.Model):
    name = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    description = models.CharField(max_length=250, null=True, blank=True)
    image_path = models.CharField(max_length=250, null=True, blank=True)
    quantity = models.FloatField(null=True, blank=True)
    last_updated_time = models.DateTimeField(auto_now=True, null=True, blank=True)

    def __str__(self):
        return self.name if self.name else "Unnamed Item"


class Sample(models.Model):
    name = models.CharField(max_length=100, db_index=True, null=True, blank=True)
    estimated_hour = models.TimeField(null=True, blank=True)
    estomated_min = models.TimeField(null=True, blank=True)
    break_out_time = models.TimeField(null=True, blank=True)
    sample_status = models.BooleanField(null=True, blank=True)
    batch = models.ForeignKey(
        'Batch',
        on_delete=models.CASCADE,
        related_name='samples',
        null=True,
        blank=True
    )

    def __str__(self):
        return self.name if self.name else "Unnamed Sample"


class User(models.Model):
    username = models.CharField(max_length=50, unique=True, db_index=True, null=True, blank=True)
    password = models.CharField(max_length=128, null=True, blank=True)
    batch_no = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.username if self.username else "Unnamed User"
