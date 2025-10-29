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
from .models import Inventory, Batch
from .serializers import InventorySerializer, BatchSerializer


# -------------------- INVENTORY API --------------------
class AddInventoryAPIView(APIView):
    def post(self, request):
        """Add a new inventory item"""
        serializer = InventorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {"message": "Inventory item added successfully", "data": serializer.data},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request):
        """Get all inventory items"""
        items = Inventory.objects.all()
        serializer = InventorySerializer(items, many=True)
        return Response({"data": serializer.data}, status=status.HTTP_200_OK)


# -------------------- UPDATE INVENTORY API --------------------
class UpdateInventoryAPIView(APIView):
    def put(self, request, pk):
        """Update an existing inventory item completely."""
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
        """Partially update an inventory item."""
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


# -------------------- BATCH API --------------------
from rest_framework import generics

class BatchCreateAPIView(generics.ListCreateAPIView):
    """Handles both GET (list) and POST (create) for batches"""
    queryset = Batch.objects.all()
    serializer_class = BatchSerializer


import cv2
import threading
from django.http import StreamingHttpResponse, JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators import gzip


# ===============================
# CAMERA CLASS
# ===============================
class VideoCamera:
    def __init__(self, camera_index=0):
        # self.cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)  # CAP_DSHOW for Windows, remove for Linux
        self.cap = cv2.VideoCapture(0)
        
        if not self.cap.isOpened():
            raise RuntimeError("Could not open USB camera.")

        # Optional settings
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
        self.cap.set(cv2.CAP_PROP_FPS, 40)

        self.frame = None
        self.is_running = True

        # Start thread
        thread = threading.Thread(target=self.update, daemon=True)
        thread.start()

    def update(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if ret:
                self.frame = frame

    def get_frame(self):
        if self.frame is None:
            return None
        ret, jpeg = cv2.imencode('.jpg', self.frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
        return jpeg.tobytes()

    def stop(self):
        self.is_running = False
        self.cap.release()


# Global camera instance
camera_instance = None


# ===============================
# STREAM GENERATOR
# ===============================
def generate_frames():
    global camera_instance
    if camera_instance is None:
        camera_instance = VideoCamera(0)

    while True:
        frame = camera_instance.get_frame()
        if frame is None:
            continue
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


# ===============================
# STREAM VIEW (MJPEG)
# ===============================
@method_decorator(gzip.gzip_page, name='dispatch')
class CameraStreamAPIView(View):
    def get(self, request):
        global camera_instance
        try:
            if camera_instance is None:
                camera_instance = VideoCamera(0)
            return StreamingHttpResponse(
                generate_frames(),
                content_type='multipart/x-mixed-replace; boundary=frame'
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)


# ===============================
# STATUS VIEW (JSON)
# ===============================
from datetime import datetime

class CameraStatusAPIView(View):
    def get(self, request):
        global camera_instance

        # Check camera status
        camera_status = "disconnected"
        resolution = None
        fps = None

        if camera_instance and camera_instance.cap.isOpened():
            camera_status = "connected"
            width = int(camera_instance.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(camera_instance.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = int(camera_instance.cap.get(cv2.CAP_PROP_FPS))
            resolution = f"{width}x{height}"

        # Dummy robot status (You can replace this with actual logic later)
        robot_status = "active" if camera_status == "connected" else "idle"

        # Current server time
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Return combined JSON
        return JsonResponse({
            "camera": {
                "status": camera_status,
                "resolution": resolution,
                "fps": fps
            },
            "robot": {
                "status": robot_status
            },
            "time": current_time
        }, status=200)
