from django.conf.urls.i18n import i18n_patterns
from django.views.static import serve
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include, re_path
from user_app.secure_media import secure_media_view

# 1. i18n URL (til prefiksisiz) - TO'G'RI
urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
]

# 2. Media va Static (til prefiksisiz)
# XAVFSIZLIK: Barcha media fayllar secure_media_view orqali xizmat ko'rsatiladi
# Bu CWE-200 (Information Disclosure) va Broken Access Control zaifliklarini oldini oladi
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', secure_media_view, name='secure_media'),
    re_path(r'^static/(?P<path>.*)$', serve, {'document_root': settings.STATIC_ROOT}),
]

# 3. Barcha boshqa URL'lar (til prefiksli)
urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
    path('captcha/', include('captcha.urls')),
    path('', include('article_app.urls')),
    path('profile/', include('user_app.urls')),
    path('journal/', include('journal.urls')),
    path('post/', include('post.urls')),
    path('fileapp/', include('fileapp.urls')),
    path('test_maker/', include('test_maker.urls')),
    path('expert/', include('expert.urls')),
    path('moderator/', include('moderator.urls')),
    path('question/', include('question.urls')),
    path('pupil/', include('pupil.urls')),
    path('exam/', include('exam.urls')),
    path('admin1/', include('admin1.urls')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

handler404 = 'user_app.views.error_404'
handler500 = 'user_app.views.error_500'