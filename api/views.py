from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.hashers import make_password, check_password
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import User
from .serializers import *


@method_decorator(csrf_exempt, name='dispatch')
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            batch_no = data.get('batch_no')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)

            if User.objects.filter(username=username).exists():
                return JsonResponse({'error': 'Username already exists'}, status=400)

            hashed_password = make_password(password)
            user = User.objects.create(username=username, password=hashed_password, batch_no=batch_no)
            return JsonResponse({'message': 'User registered successfully', 'user_id': user.id}, status=201)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')

            if not username or not password:
                return JsonResponse({'error': 'Username and password are required'}, status=400)

            user = User.objects.filter(username=username).first()
            if user and check_password(password, user.password):
                return JsonResponse({'message': 'Login successful', 'user_id': user.id}, status=200)
            else:
                return JsonResponse({'error': 'Invalid username or password'}, status=401)

        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Inventory
from .serializers import InventorySerializer

class AddInventoryAPIView(APIView):
    def post(self, request):
        serializer = InventorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Inventory item added successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Inventory
from .serializers import InventorySerializer


class UpdateInventoryAPIView(APIView):
    def put(self, request, pk):
        """
        Update an existing inventory item completely.
        (All fields should be sent in the request)
        """
        try:
            item = Inventory.objects.get(pk=pk)
        except Inventory.DoesNotExist:
            return Response({"error": "Inventory item not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = InventorySerializer(item, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Inventory item updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        """
        Partially update an inventory item (only send fields you want to change).
        """
        try:
            item = Inventory.objects.get(pk=pk)
        except Inventory.DoesNotExist:
            return Response({"error": "Inventory item not found"}, status=status.HTTP_404_NOT_FOUND)

        serializer = InventorySerializer(item, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Inventory item partially updated successfully", "data": serializer.data},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# class CreateSampleWithEstimationAPIView(APIView):
#     def post(self, request):
#         """
#         Create a sample using breakout_time as primary, with estimated hour/min as reference.
#         Example JSON:
#         {
#             "batch_id": 1,
#             "name": "Sample X",
#             "break_out_time": "10:00:00",
#             "estimated_hour": "02:00:00",
#             "estomated_min": "00:30:00",
#             "sample_status": false
#         }
#         """
#         data = request.data

#         batch_id = data.get("batch_id")
#         if not batch_id:
#             return Response({"error": "batch_id is required"}, status=status.HTTP_400_BAD_REQUEST)

#         try:
#             batch = Batch.objects.get(id=batch_id)
#         except Batch.DoesNotExist:
#             return Response({"error": "Batch not found"}, status=status.HTTP_404_NOT_FOUND)

#         serializer = SampleSerializer(data={**data, "batch": batch.id})
#         if serializer.is_valid():
#             sample = serializer.save()
#             return Response(
#                 {
#                     "message": "Sample created successfully",
#                     "sample": SampleSerializer(sample).data
#                 },
#                 status=status.HTTP_201_CREATED
#             )
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
from rest_framework import generics
from .models import Batch
from .serializers import BatchSerializer
    

class BatchCreateAPIView(generics.CreateAPIView):
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer