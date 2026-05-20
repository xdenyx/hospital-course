from django.contrib import admin
from django.urls import path, include
from hospital.views import api_login, api_logout 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('hospital.api.urls')), 
    path('api/login/', api_login, name='api-login'),
    path('api/logout/', api_logout, name='api-logout'),
]