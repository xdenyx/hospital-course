from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

@api_view(['POST'])
@permission_classes([AllowAny])
def api_login(request):
    """
    Принимает логин и пароль в формате JSON, 
    проверяет их и возвращает токен авторизации.
    """
    username = request.data.get('username')
    password = request.data.get('password')
    user = authenticate(username=username, password=password)
    
    if user is not None:
        # Создаем или получаем существующий токен для пользователя
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'is_admin': user.is_staff or user.is_superuser
        }, status=status.HTTP_200_OK)
        
    return Response(
        {'error': "Неправильне ім'я користувача або пароль"}, 
        status=status.HTTP_400_BAD_REQUEST
    )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    # Удаляет токен пользователя на стороне сервера
    try:
        request.user.auth_token.delete()
        return Response({'success': 'Успішно вийшли з системи'}, status=status.HTTP_200_OK)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)