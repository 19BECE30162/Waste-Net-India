from rest_framework import status, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model, authenticate
from .serializers import UserSerializer, CustomTokenObtainPairSerializer, UserProfileSerializer

User = get_user_model()

class RegisterView(APIView):
    """
    Register a new user
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'message': 'User registered successfully',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'address': user.address
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LoginView(APIView):
    """
    Login a user and return JWT tokens
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        username_or_phone = request.data.get('username_or_phone', '').strip()
        password = request.data.get('password', '').strip()
        
        if not username_or_phone or not password:
            return Response(
                {'error': 'Please provide both username/phone and password'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = None
        
        # Try to authenticate with username first
        user = authenticate(username=username_or_phone, password=password)
        
        # If username didn't work, try email
        if user is None and '@' in username_or_phone:
            try:
                user = User.objects.get(email=username_or_phone)
                user = authenticate(username=user.username, password=password)
            except User.DoesNotExist:
                pass
        
        # If still not found, try phone number
        if user is None:
            try:
                user = User.objects.get(phone_number=username_or_phone)
                user = authenticate(username=user.username, password=password)
            except User.DoesNotExist:
                pass
        
        if user is not None and user.is_active:
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Login successful',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'address': user.address or ''
                },
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            }, status=status.HTTP_200_OK)
        
        # Log the failed attempt for debugging
        print(f"Failed login attempt for: {username_or_phone}")
        return Response(
            {'error': 'Invalid username/phone/email or password'},
            status=status.HTTP_401_UNAUTHORIZED
        )

class UserProfileView(APIView):
    """
    Get or update user profile
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)
    
    def put(self, request):
        serializer = UserProfileSerializer(
            request.user, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Custom token obtain view that uses our custom token serializer
    """
    serializer_class = CustomTokenObtainPairSerializer
