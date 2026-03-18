from django.urls import path
from . import views

app_name = 'resumos'

urlpatterns = [
    path('', views.lista_resumos, name='lista'),
    path('signup/', views.signup, name='signup'),
    path('verificar-email/<str:token>/', views.verificar_email, name='verificar_email'),
    path('resumo/<int:pk>/', views.detalhe_resumo, name='detalhe'),
    path('criar/', views.criar_resumo, name='criar'),
    path('resumo/<int:pk>/editar/', views.editar_resumo, name='editar'),
    path('resumo/<int:pk>/apagar/', views.apagar_resumo, name='apagar'),
    path('perfil/<str:username>/', views.perfil_usuario, name='perfil'),
    path('api/disciplinas-por-ano/', views.get_disciplinas_por_ano, name='disciplinas_por_ano'),
]