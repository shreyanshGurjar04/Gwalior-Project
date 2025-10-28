from django.urls import path
from .views import (
    RegisterView, LoginView,
    AddInventoryAPIView, UpdateInventoryAPIView,
    CreateSampleWithEstimationAPIView,
    BatchCreateAPIView
)

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),

    # Inventory APIs
    path('inventory/add/', AddInventoryAPIView.as_view(), name='add_inventory'),
    path('inventory/update/<int:pk>/', UpdateInventoryAPIView.as_view(), name='update_inventory'),

    # Sample APIs
    # path('samples/create_with_estimation/', CreateSampleWithEstimationAPIView.as_view(), name='create_sample_estimation'),
    path('batches/add/', BatchCreateAPIView.as_view(), name='batch-create'),

]
