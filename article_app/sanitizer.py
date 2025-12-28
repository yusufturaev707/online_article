"""
XSS hujumlaridan himoya qilish uchun sanitizer funksiyalar.
Bu modul input ma'lumotlarni tozalash uchun ishlatiladi.
"""
import re
import html
import bleach
from django.conf import settings


# Ruxsat etilgan HTML teglar (maqola kontenti uchun)
ALLOWED_TAGS_CONTENT = [
    'p', 'b', 'i', 'u', 'em', 'strong', 'a', 'br', 'hr',
    'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
    'table', 'thead', 'tbody', 'tr', 'th', 'td',
    'img', 'div', 'span', 'sub', 'sup',
]

# Sarlavha va keywords uchun - hech qanday HTML teglar ruxsat etilmaydi
ALLOWED_TAGS_PLAIN = []

ALLOWED_ATTRIBUTES = {
    '*': ['class', 'style', 'id'],
    'a': ['href', 'title', 'target', 'rel'],
    'img': ['src', 'alt', 'title', 'width', 'height'],
    'table': ['border', 'cellpadding', 'cellspacing'],
    'td': ['colspan', 'rowspan'],
    'th': ['colspan', 'rowspan'],
}

ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']

# XSS pattern larni aniqlash uchun regex
XSS_PATTERNS = [
    re.compile(r'<script[^>]*>.*?</script>', re.IGNORECASE | re.DOTALL),
    re.compile(r'javascript:', re.IGNORECASE),
    re.compile(r'vbscript:', re.IGNORECASE),
    re.compile(r'on\w+\s*=', re.IGNORECASE),  # onclick, onerror, etc.
    re.compile(r'expression\s*\(', re.IGNORECASE),  # CSS expression
    re.compile(r'url\s*\(\s*["\']?\s*javascript:', re.IGNORECASE),
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


def sanitize_plain_text(value):
    """
    Oddiy matn uchun - barcha HTML teglarni olib tashlaydi.
    Sarlavha, keywords va boshqa oddiy matn maydonlari uchun.
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

    return cleaned.strip()


def sanitize_html_content(value):
    """
    HTML kontenti uchun - faqat ruxsat etilgan teglarni qoldiradi.
    Abstract va boshqa rich text maydonlari uchun.
    """
    if not value:
        return ''

    cleaned = bleach.clean(
        str(value),
        tags=ALLOWED_TAGS_CONTENT,
        attributes=ALLOWED_ATTRIBUTES,
        protocols=ALLOWED_PROTOCOLS,
        strip=True,
        strip_comments=True
    )

    return cleaned.strip()


def sanitize_title(value):
    """
    Maqola sarlavhasi uchun maxsus sanitizer.
    Hech qanday HTML teglar ruxsat etilmaydi.
    """
    if not value:
        return ''

    # Avval barcha HTML teglarni olib tashlash
    cleaned = bleach.clean(str(value), tags=[], strip=True, strip_comments=True)

    # HTML entities ni decode va encode qilish
    cleaned = html.unescape(cleaned)

    # Xavfli belgilarni escape qilish
    cleaned = html.escape(cleaned)

    # Ortiqcha bo'shliqlarni tozalash
    cleaned = ' '.join(cleaned.split())

    return cleaned.strip()


def sanitize_keywords(value):
    """
    Kalit so'zlar uchun sanitizer.
    """
    return sanitize_title(value)


def sanitize_abstract(value):
    """
    Annotatsiya (abstract) uchun sanitizer.
    Ba'zi HTML teglar ruxsat etiladi.
    """
    return sanitize_html_content(value)


def validate_and_sanitize(value, field_type='plain'):
    """
    Umumiy validatsiya va sanitizatsiya funksiyasi.

    Args:
        value: Tozalanadigan qiymat
        field_type: 'plain', 'title', 'keywords', 'abstract', 'html'

    Returns:
        tuple: (is_valid, sanitized_value, error_message)
    """
    if not value:
        return True, '', None

    # XSS mavjudligini tekshirish
    if contains_xss(value):
        # Log qilish mumkin
        pass

    # Field turiga qarab sanitizatsiya
    sanitizers = {
        'plain': sanitize_plain_text,
        'title': sanitize_title,
        'keywords': sanitize_keywords,
        'abstract': sanitize_abstract,
        'html': sanitize_html_content,
    }

    sanitizer = sanitizers.get(field_type, sanitize_plain_text)
    sanitized = sanitizer(value)

    return True, sanitized, None
