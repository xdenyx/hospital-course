from django.contrib import admin
from django.urls import path, include
from hospital.views import index_view, login_view, logout_view

urlpatterns = [
    path('admin/', admin.site.urls),
    
    path('api/', include('hospital.api.urls')), 

    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),

    path('', index_view, name='index'), 
]