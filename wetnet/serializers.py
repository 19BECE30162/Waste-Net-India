from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        write_only=True, 
        required=True, 
        style={'input_type': 'password'},
        min_length=8,
        validators=[validate_password]
    )
    confirm_password = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'},
        min_length=8
    )
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'confirm_password', 'phone_number', 'address']
        read_only_fields = ['id']
        extra_kwargs = {
            'email': {'required': True}
        }
    
    def validate(self, data):
        if data['password'] != data.pop('confirm_password'):
            raise serializers.ValidationError({"confirm_password": "Password fields didn't match."})
        return data
    
    def create(self, validated_data):
        # Remove confirm_password from the data before creating the user
        validated_data.pop('confirm_password', None)
        
        try:
            # Create user with create_user to handle password hashing
            user = User.objects.create_user(
                username=validated_data['username'],
                email=validated_data['email'],
                password=validated_data['password'],  # This will be hashed by create_user
                phone_number=validated_data.get('phone_number', ''),
                address=validated_data.get('address', '')
            )
            return user
        except Exception as e:
            # Log the error for debugging
            print(f"Error creating user: {str(e)}")
            raise serializers.ValidationError({"error": "Failed to create user. Please try again."})

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'phone_number', 'address']
        read_only_fields = ['id', 'username', 'email']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['username'] = user.username
        token['email'] = user.email
        return token
