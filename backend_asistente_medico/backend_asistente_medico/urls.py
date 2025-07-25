from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authentication.urls')),
    path('asistente/atender/', views.atender_paciente, name='atender_paciente'),
    path('transcribir-audio/', views.transcribir_audio, name='transcribir_audio'),
    path('procesar-consulta-voz/', views.procesar_consulta_voz, name='procesar_consulta_voz'),
    path('generar-audio/', views.generar_audio_respuesta, name='generar_audio'),
]
