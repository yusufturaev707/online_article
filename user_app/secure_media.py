"""
Xavfsiz media fayllarini yuklash moduli.
CWE-200 (Information Disclosure) va Broken Access Control zaifliklarini oldini olish.

Bu modul maxfiy fayllarni faqat autentifikatsiya qilingan va
ruxsat berilgan foydalanuvchilarga taqdim etadi.
"""
import os
import mimetypes
import logging
from pathlib import Path

from django.conf import settings
from django.http import HttpResponse, HttpResponseForbidden, HttpResponseNotFound, FileResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_GET
from django.core.exceptions import PermissionDenied

logger = logging.getLogger('security')

# Himoyalangan papkalar - faqat autentifikatsiya qilingan foydalanuvchilar kirishi mumkin
PROTECTED_FOLDERS = [
    'questions/',
    'documents/',
    'question_templates/',
    'payments/',
    'files/reviewer/',
    'files/template/',
    'uploads/',
]

# Roli bo'yicha ruxsat etilgan papkalar
ROLE_BASED_ACCESS = {
    'questions/': ['admin', 'expert', 'moderator', 'teacher'],
    'documents/': ['admin', 'expert', 'moderator', 'teacher'],
    'question_templates/': ['admin', 'expert', 'moderator', 'teacher'],
    'payments/': ['admin', 'moderator'],
    'files/reviewer/': ['admin', 'editor', 'reviewer'],
    'files/template/': ['admin', 'editor', 'author'],
    'uploads/': ['admin', 'editor', 'reviewer', 'author'],
}


def get_user_roles(user):
    """Foydalanuvchi rollarini olish"""
    roles = []
    if hasattr(user, 'chosen_role') and user.chosen_role:
        roles.append(user.chosen_role.code_name)

    # Qo'shimcha rollarni tekshirish
    if user.is_superuser:
        roles.append('admin')

    return roles


def is_path_allowed(file_path, user_roles):
    """
    Berilgan yo'l uchun foydalanuvchi ruxsatini tekshirish.
    """
    normalized_path = file_path.replace('\\', '/')

    for folder, allowed_roles in ROLE_BASED_ACCESS.items():
        if folder in normalized_path:
            # Foydalanuvchi rollaridan birortasi ruxsat etilganlar ro'yxatida bormi
            for role in user_roles:
                if role in allowed_roles:
                    return True
            return False

    # Agar maxsus qoida bo'lmasa, himoyalangan papka ekanligini tekshirish
    for folder in PROTECTED_FOLDERS:
        if folder in normalized_path:
            return False  # Himoyalangan, lekin rol aniqlanmagan

    return True  # Himoyalanmagan papka - ruxsat berilgan


def is_protected_path(file_path):
    """Yo'l himoyalangan papkada joylashganligini tekshirish"""
    normalized_path = file_path.replace('\\', '/')

    for folder in PROTECTED_FOLDERS:
        if folder in normalized_path:
            return True
    return False


def sanitize_path(path):
    """
    Yo'lni xavfsiz qilish - path traversal hujumlarini oldini olish.
    """
    # Xavfli belgilarni tekshirish
    if '..' in path or path.startswith('/') or path.startswith('\\'):
        return None

    # Normalizatsiya qilish
    normalized = os.path.normpath(path)

    # Yana bir marta '..' tekshirish (normalizatsiyadan keyin)
    if '..' in normalized:
        return None

    return normalized


@require_GET
def secure_media_view(request, path):
    """
    Xavfsiz media fayllarini yuklash view.

    Bu view:
    1. Path traversal hujumlarini oldini oladi
    2. Himoyalangan fayllar uchun autentifikatsiyani tekshiradi
    3. Rol asosida ruxsatni tekshiradi
    4. Xavfsiz tarzda faylni taqdim etadi
    """
    # Path sanitization
    safe_path = sanitize_path(path)
    if safe_path is None:
        logger.warning(f"Path traversal urinishi aniqlandi: {path}, IP: {get_client_ip(request)}")
        return HttpResponseForbidden("Noto'g'ri yo'l")

    # To'liq fayl yo'lini yaratish
    full_path = os.path.join(settings.MEDIA_ROOT, safe_path)

    # Fayl mavjudligini tekshirish
    if not os.path.exists(full_path) or not os.path.isfile(full_path):
        return HttpResponseNotFound("Fayl topilmadi")

    # Yo'l MEDIA_ROOT ichida ekanligini tekshirish (qo'shimcha xavfsizlik)
    try:
        real_path = os.path.realpath(full_path)
        media_root_real = os.path.realpath(settings.MEDIA_ROOT)
        if not real_path.startswith(media_root_real):
            logger.warning(f"Media root dan tashqariga chiqish urinishi: {path}")
            return HttpResponseForbidden("Ruxsat berilmagan")
    except Exception:
        return HttpResponseForbidden("Xatolik")

    # Himoyalangan yo'l ekanligini tekshirish
    if is_protected_path(safe_path):
        # Autentifikatsiya talab qilinadi
        if not request.user.is_authenticated:
            logger.info(f"Autentifikatsiyasiz himoyalangan faylga kirish urinishi: {path}")
            return HttpResponseForbidden("Kirish uchun tizimga kiring")

        # Rolni tekshirish
        user_roles = get_user_roles(request.user)
        if not is_path_allowed(safe_path, user_roles):
            logger.warning(
                f"Ruxsatsiz fayl kirish urinishi: {path}, "
                f"Foydalanuvchi: {request.user.username}, "
                f"Rollar: {user_roles}"
            )
            return HttpResponseForbidden("Bu faylga kirish huquqingiz yo'q")

    # Faylni xavfsiz taqdim etish
    try:
        # MIME turini aniqlash
        content_type, _ = mimetypes.guess_type(full_path)
        if content_type is None:
            content_type = 'application/octet-stream'

        # FileResponse orqali xavfsiz yuklash
        response = FileResponse(
            open(full_path, 'rb'),
            content_type=content_type
        )

        # Xavfsizlik headerlari
        response['X-Content-Type-Options'] = 'nosniff'
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(full_path)}"'

        # Kesh boshqaruvi - himoyalangan fayllar uchun kesh o'chirish
        if is_protected_path(safe_path):
            response['Cache-Control'] = 'private, no-cache, no-store, must-revalidate'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'

        return response

    except IOError:
        logger.error(f"Fayl o'qishda xatolik: {full_path}")
        return HttpResponseNotFound("Fayl o'qib bo'lmadi")


def get_client_ip(request):
    """Mijoz IP manzilini olish"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip
