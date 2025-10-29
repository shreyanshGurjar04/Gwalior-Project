from django.urls import path
from .views import *

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    # Inventory APIs
    path('inventory/add/', AddInventoryAPIView.as_view(), name='add_inventory'),
    path('inventory/update/<int:pk>/', UpdateInventoryAPIView.as_view(), name='update_inventory'),

    # Batch APIs
    path('batches/add/', BatchCreateAPIView.as_view(), name='batch-create'),

    # camera feed
    path('camera/stream/', CameraStreamAPIView.as_view(), name='camera_stream'),
    path('camera/status/', CameraStatusAPIView.as_view(), name='camera_status'),
]
