import re
import html


def clean_html(raw_html: str) -> str:
    """
    Удаляет HTML-теги и заменяет спецсимволы (&nbsp;, &lt;, &gt; и т.д.)
    """
    if not raw_html:
        return ""

    # заменяем html спецсимволы
    text = html.unescape(raw_html)

    # убираем теги <br>, <p> заменяя их на перенос строки
    text = re.sub(r'<\s*br\s*/?>', '\n', text, flags=re.IGNORECASE)
    text = re.sub(r'<\s*/?p\s*>', '\n', text, flags=re.IGNORECASE)

    # убираем все остальные html теги
    text = re.sub(r'<[^>]+>', '', text)

    # убираем лишние пробелы и пустые строки
    text = re.sub(r'\n\s*\n+', '\n\n', text).strip()

    return text