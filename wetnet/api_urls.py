from django.urls import path
from . import api_views

app_name = 'api'

urlpatterns = [
    # Authentication endpoints
    path('register/', api_views.RegisterView.as_view(), name='register'),
    path('login/', api_views.LoginView.as_view(), name='login'),
    path('token/', api_views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # User profile endpoints
    path('profile/', api_views.UserProfileView.as_view(), name='user_profile'),
]
