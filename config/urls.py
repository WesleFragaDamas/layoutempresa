from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Certifique-se de que o namespace está aqui:
    path('app/', include('maquinas.urls', namespace='maquinas')),

    path('login/', auth_views.LoginView.as_view(template_name='maquinas/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    # ... (URLs de password_reset, se você as manteve) ...
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='maquinas/password_reset_form.html', email_template_name='maquinas/password_reset_email.html', subject_template_name='maquinas/password_reset_subject.txt'), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='maquinas/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='maquinas/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='maquinas/password_reset_complete.html'), name='password_reset_complete'),

    # Redirecionamento da raiz usando o namespace
    path('', lambda request: redirect('maquinas:layout_empresa_padrao', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)