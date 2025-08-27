from django.urls import path, re_path, include
from . import views
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('/<uuid:conversation_id>',
         views.ChatView.as_view(), name="chat_page")
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
