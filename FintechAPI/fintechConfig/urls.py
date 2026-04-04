from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView


urlpatterns = [
    path('admin/', admin.site.urls),

    #application routes
    path('api/users/', include('users.urls')),
    path('api/records/', include('records.urls')),
    path('api/dashboard/', include('analytics.urls')),

    # OpenAPI Config
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]




