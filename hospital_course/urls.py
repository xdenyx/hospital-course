from django.contrib import admin
from django.urls import path, include
from hospital.views import api_logout 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('hospital.api.urls')), 
    path('api/logout/', api_logout, name='api-logout'),
]