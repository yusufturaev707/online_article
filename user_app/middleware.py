"""
Session xavfsizlik middleware - harakatsizlik vaqtini tekshiradi.
Foydalanuvchi ma'lum vaqt davomida harakatsiz bo'lsa, sessiyani tugatadi.
"""
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.utils import timezone


class SessionInactivityMiddleware:
    """
    Foydalanuvchi harakatsizligini tekshiruvchi middleware.

    Har bir so'rovda oxirgi faoliyat vaqtini tekshiradi.
    Agar SESSION_INACTIVITY_TIMEOUT daqiqadan ko'p vaqt o'tgan bo'lsa,
    foydalanuvchini tizimdan chiqaradi.
    """

    def __init__(self, get_response):
        self.get_response = get_response
        # Timeout daqiqada (default 15 daqiqa)
        self.inactivity_timeout = getattr(settings, 'SESSION_INACTIVITY_TIMEOUT', 15)

    def __call__(self, request):
        # Faqat autentifikatsiya qilingan foydalanuvchilar uchun tekshirish
        if request.user.is_authenticated:
            current_time = timezone.now()

            # Oxirgi faoliyat vaqtini olish
            last_activity = request.session.get('last_activity')

            if last_activity:
                # String formatdan datetime ga o'tkazish
                try:
                    last_activity_time = datetime.fromisoformat(last_activity)
                    if timezone.is_naive(last_activity_time):
                        last_activity_time = timezone.make_aware(last_activity_time)

                    # Harakatsizlik vaqtini hisoblash
                    inactivity_duration = current_time - last_activity_time
                    timeout_delta = timedelta(minutes=self.inactivity_timeout)

                    if inactivity_duration > timeout_delta:
                        # Session muddati tugadi - foydalanuvchini chiqarish
                        self._logout_user(request)

                        # AJAX so'rovlari uchun maxsus javob
                        if self._is_ajax(request):
                            from django.http import JsonResponse
                            return JsonResponse({
                                'session_expired': True,
                                'message': 'Sessiya muddati tugadi. Qayta kiring.',
                                'redirect_url': '/login/'
                            }, status=401)

                        # Oddiy so'rovlar uchun login sahifasiga yo'naltirish
                        return redirect('login')

                except (ValueError, TypeError):
                    # Xato bo'lsa, yangi vaqtni o'rnatish
                    pass

            # Oxirgi faoliyat vaqtini yangilash
            request.session['last_activity'] = current_time.isoformat()

        response = self.get_response(request)
        return response

    def _logout_user(self, request):
        """Foydalanuvchini xavfsiz tarzda chiqarish"""
        # Session ma'lumotlarini o'chirish
        session_key = request.session.session_key

        # Logout qilish
        logout(request)

        # Eski session kalit bilan bog'liq ma'lumotlarni o'chirish
        if session_key:
            from django.contrib.sessions.models import Session
            try:
                Session.objects.filter(session_key=session_key).delete()
            except Exception:
                pass

    def _is_ajax(self, request):
        """AJAX so'rovini aniqlash"""
        return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


class SessionSecurityMiddleware:
    """
    Qo'shimcha session xavfsizlik tekshiruvlari.

    - IP manzili o'zgarishini tekshirish
    - User-Agent o'zgarishini tekshirish
    - Session hijacking oldini olish
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            current_ip = self._get_client_ip(request)
            current_ua = request.META.get('HTTP_USER_AGENT', '')[:200]  # Uzunligini cheklash

            # Session da saqlangan qiymatlarni olish
            session_ip = request.session.get('session_ip')
            session_ua = request.session.get('session_user_agent')

            # Birinchi marta - qiymatlarni saqlash
            if not session_ip:
                request.session['session_ip'] = current_ip
                request.session['session_user_agent'] = current_ua
            else:
                # IP o'zgargan bo'lsa - session ni yakunlash
                if session_ip != current_ip:
                    self._handle_suspicious_activity(request, 'IP manzili o'zgardi')
                    logout(request)
                    request.session.flush()
                    return redirect('login')

                # User-Agent keskin o'zgargan bo'lsa - session ni yakunlash
                if session_ua and current_ua:
                    # Asosiy qismi o'zgarmagan bo'lsa ruxsat berish (minor updates)
                    if not self._similar_user_agents(session_ua, current_ua):
                        self._handle_suspicious_activity(request, 'User-Agent o\'zgardi')
                        logout(request)
                        request.session.flush()
                        return redirect('login')

        response = self.get_response(request)
        return response

    def _get_client_ip(self, request):
        """Mijoz IP manzilini olish"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR', '')
        return ip

    def _similar_user_agents(self, ua1, ua2):
        """Ikki User-Agent o'xshashligini tekshirish"""
        # Asosiy brauzer va OS ma'lumotlari bir xil bo'lsa True
        # Bu minor version yangilanishlarida foydalanuvchini chiqarmaslik uchun
        if not ua1 or not ua2:
            return True

        # Birinchi 50 belgi bir xil bo'lsa (odatda brauzer va OS nomi)
        return ua1[:50] == ua2[:50]

    def _handle_suspicious_activity(self, request, reason):
        """Shubhali faoliyatni qayd qilish"""
        import logging
        logger = logging.getLogger('security')

        try:
            logger.warning(
                f"Shubhali faoliyat aniqlandi: {reason}. "
                f"Foydalanuvchi: {request.user.username}, "
                f"IP: {self._get_client_ip(request)}"
            )
        except Exception:
            pass
