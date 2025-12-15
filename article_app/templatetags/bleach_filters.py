import bleach
from django import template
from django.conf import settings
from django.utils.safestring import mark_safe

register = template.Library()


@register.filter(name='bleach_clean')
def bleach_clean(value):
    """
    XSS hujumlaridan himoya qiluvchi filter.
    Faqat ruxsat etilgan HTML teglarini qoldiradi.

    Usage: {{ content|bleach_clean }}
    """
    if value is None:
        return ''

    allowed_tags = getattr(settings, 'BLEACH_ALLOWED_TAGS', [
        'p', 'b', 'i', 'u', 'em', 'strong', 'a', 'br', 'hr',
        'ul', 'ol', 'li', 'blockquote', 'code', 'pre',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'table', 'thead', 'tbody', 'tr', 'th', 'td',
        'img', 'div', 'span', 'sub', 'sup',
    ])

    allowed_attributes = getattr(settings, 'BLEACH_ALLOWED_ATTRIBUTES', {
        '*': ['class', 'style', 'id'],
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        'table': ['border', 'cellpadding', 'cellspacing'],
        'td': ['colspan', 'rowspan'],
        'th': ['colspan', 'rowspan'],
    })

    allowed_protocols = getattr(settings, 'BLEACH_ALLOWED_PROTOCOLS', ['http', 'https', 'mailto'])

    strip = getattr(settings, 'BLEACH_STRIP_TAGS', True)
    strip_comments = getattr(settings, 'BLEACH_STRIP_COMMENTS', True)

    cleaned = bleach.clean(
        str(value),
        tags=allowed_tags,
        attributes=allowed_attributes,
        protocols=allowed_protocols,
        strip=strip,
        strip_comments=strip_comments
    )

    return mark_safe(cleaned)


@register.filter(name='bleach_linkify')
def bleach_linkify(value):
    """
    Matndagi URL larni avtomatik link qiladi va XSS dan himoya qiladi.

    Usage: {{ content|bleach_linkify }}
    """
    if value is None:
        return ''

    # Avval tozalash
    cleaned = bleach_clean(value)

    # Keyin linkify
    linkified = bleach.linkify(cleaned)

    return mark_safe(linkified)


@register.filter(name='strip_tags_safe')
def strip_tags_safe(value):
    """
    Barcha HTML teglarni olib tashlaydi (faqat matn qoldiradi).

    Usage: {{ content|strip_tags_safe }}
    """
    if value is None:
        return ''

    return bleach.clean(str(value), tags=[], strip=True)
