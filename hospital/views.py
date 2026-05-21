from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    # Удаляет токен пользователя на стороне сервера
    try:
        request.user.auth_token.delete()
        return Response({'success': 'Успішно вийшли з системи'}, status=status.HTTP_200_OK)
    except Exception:
        return Response(status=status.HTTP_400_BAD_REQUEST)