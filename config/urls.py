from django.contrib import admin
from django.urls import path, include # Adicione include
from django.contrib.auth import views as auth_views # Views de autenticação do Django
from django.shortcuts import redirect # Para redirecionar a raiz

urlpatterns = [
    path('admin/', admin.site.urls),

    # Inclui as URLs da app 'maquinas' sob o prefixo 'app/'
    path('app/', include('maquinas.urls', namespace='maquinas')),

    # URLs de Autenticação do Django
    path('login/', auth_views.LoginView.as_view(
        template_name='maquinas/login.html'
        ), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),

    # --- NOVAS URLS PARA REDEFINIÇÃO DE SENHA ---
    path('password_reset/',
         auth_views.PasswordResetView.as_view(
            template_name='maquinas/password_reset_form.html', # Você precisará criar este template
            email_template_name='maquinas/password_reset_email.html', # E este
            subject_template_name='maquinas/password_reset_subject.txt' # E este
            # success_url pode ser definido aqui ou o padrão será 'password_reset_done'
         ),
         name='password_reset'),
    path('password_reset/done/',
         auth_views.PasswordResetDoneView.as_view(
            template_name='maquinas/password_reset_done.html' # Você precisará criar este template
         ),
         name='password_reset_done'),
    path('reset/<uidb64>/<token>/',
         auth_views.PasswordResetConfirmView.as_view(
            template_name='maquinas/password_reset_confirm.html' # Você precisará criar este template
            # success_url pode ser definido aqui ou o padrão será 'password_reset_complete'
         ),
         name='password_reset_confirm'),
    path('reset/done/',
         auth_views.PasswordResetCompleteView.as_view(
            template_name='maquinas/password_reset_complete.html' # Você precisará criar este template
         ),
         name='password_reset_complete'),
    # -------------------------------------------

    # Redirecionar a página raiz para a página de layout
    path('', lambda request: redirect('maquinas:layout_empresa', permanent=False)),
]