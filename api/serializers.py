from rest_framework import serializers
from .models import User, Batch, Sample, Inventory


class BatchSerializer(serializers.ModelSerializer):
    class Meta:
        model = Batch
        fields = '__all__'


class InventorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Inventory
        fields = '__all__'


from rest_framework import serializers
from .models import Sample
from datetime import datetime, timedelta

class SampleSerializer(serializers.ModelSerializer):
    expected_finish_time = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Sample
        fields = '__all__'

    def get_expected_finish_time(self, obj):
        """Compute expected finish time = break_out_time + estimated_hour + estimated_min"""
        try:
            base_time = datetime.combine(datetime.today(), obj.break_out_time)
            extra_time = timedelta(
                hours=obj.estimated_hour.hour if obj.estimated_hour else 0,
                minutes=obj.estomated_min.minute if obj.estomated_min else 0
            )
            expected_time = (base_time + extra_time).time()
            return expected_time
        except Exception:
            return None


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'password', 'batch_no']
        extra_kwargs = {
            'password': {'write_only': True}  # hide password in responses
        }

    def create(self, validated_data):
        """
        Hash password before saving.
        """
        from django.contrib.auth.hashers import make_password
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)
