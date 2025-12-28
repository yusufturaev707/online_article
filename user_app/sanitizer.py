"""
XSS hujumlaridan himoya qilish uchun sanitizer funksiyalar.
user_app uchun input ma'lumotlarni tozalash.
"""
import re
import html
import bleach


# XSS pattern larni aniqlash uchun regex
XSS_PATTERNS = [
    re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'vbscript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick, onerror, etc.
    re.compile(r'expression\s*\(', re.IGNORECASE),  # CSS expression
    re.compile(r'url\s*\(\s*["\']?\s*javascript:', re.IGNORECASE),
    re.compile(r'<iframe', re.IGNORECASE),
    re.compile(r'<object', re.IGNORECASE),
    re.compile(r'<embed', re.IGNORECASE),
    re.compile(r'<svg[^>]*onload', re.IGNORECASE),
]


def contains_xss(value):
    """
    Matnda XSS pattern bor-yo'qligini tekshiradi.
    Returns: True agar XSS topilsa, False aks holda
    """
    if not value:
        return False

    for pattern in XSS_PATTERNS:
        if pattern.search(str(value)):
            return True
    return False


def sanitize_text(value):
    """
    Oddiy matn uchun sanitizer - barcha HTML teglarni olib tashlaydi.
    Username, ism, telefon, ish joyi va boshqa oddiy maydonlar uchun.
    """
    if not value:
        return ''

    # Barcha HTML teglarni olib tashlash
    cleaned = bleach.clean(
        str(value),
        tags=[],
        attributes={},
        strip=True,
        strip_comments=True
    )

    # HTML entities ni decode qilish va qayta encode qilish
    cleaned = html.unescape(cleaned)
    cleaned = html.escape(cleaned)

    # Ortiqcha bo'shliqlarni tozalash
    cleaned = ' '.join(cleaned.split())

    return cleaned.strip()


def sanitize_comment(value):
    """
    Izoh/comment uchun sanitizer.
    Ba'zi bazaviy HTML teglar ruxsat etiladi.
    """
    if not value:
        return ''

    allowed_tags = ['p', 'b', 'i', 'u', 'em', 'strong', 'br']
    allowed_attributes = {}

    cleaned = bleach.clean(
        str(value),
        tags=allowed_tags,
        attributes=allowed_attributes,
        strip=True,
        strip_comments=True
    )

    return cleaned.strip()


def sanitize_username(value):
    """
    Username uchun maxsus sanitizer.
    Faqat harflar, raqamlar va ba'zi belgilar ruxsat.
    """
    if not value:
        return ''

    # HTML teglarni olib tashlash
    cleaned = bleach.clean(str(value), tags=[], strip=True)

    # Faqat ruxsat etilgan belgilarni qoldirish
    cleaned = re.sub(r'[^\w\-_.]', '', cleaned)

    return cleaned.strip()


def sanitize_email(value):
    """
    Email uchun sanitizer.
    """
    if not value:
        return ''

    cleaned = bleach.clean(str(value), tags=[], strip=True)
    cleaned = html.unescape(cleaned)

    # Oddiy email formatini tekshirish
    email_pattern = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    if email_pattern.match(cleaned):
        return cleaned.strip()

    return cleaned.strip()


def sanitize_phone(value):
    """
    Telefon raqami uchun sanitizer.
    Faqat raqamlar va ba'zi belgilar ruxsat.
    """
    if not value:
        return ''

    cleaned = bleach.clean(str(value), tags=[], strip=True)

    # Faqat raqamlar va + - () belgilarini qoldirish
    cleaned = re.sub(r'[^\d\+\-\(\)\s]', '', cleaned)

    return cleaned.strip()


def sanitize_url(value):
    """
    URL uchun sanitizer.
    """
    if not value:
        return ''

    cleaned = bleach.clean(str(value), tags=[], strip=True)

    # javascript: va data: URLlarni bloklash
    if re.match(r'^(javascript|data|vbscript):', cleaned, re.IGNORECASE):
        return ''

    return cleaned.strip()
