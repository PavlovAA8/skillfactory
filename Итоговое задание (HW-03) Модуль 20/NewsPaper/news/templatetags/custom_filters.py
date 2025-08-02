from django import template
import re

register = template.Library()

BAD_WORDS = {'слово'}

@register.filter(name='censor_words')
def censor_words(value):
    # Проверяем, что значение строкового типа
    if not isinstance(value, str):
        return value

    def censor_match(match):
        word = match.group()
        # Проверяем что все слова, которые нужно цензурировать, начинаются с верхнего или нижнего регистра. Остальные буквы слов могут быть только в нижнем регистре.
        if len(word) > 1 and (word[0].isalpha() and word[0].lower() == word[0] or word[0].isupper()):
            # Проверяем, есть ли слово в списке запрещённых (в нижнем регистре)
            if word.lower() in BAD_WORDS:
                # Формируем цензурированное слово: первая буква + *
                return word[0] + '*' * (len(word) - 1)
        return word

    # Используем регулярное выражение для поиска слов
    pattern = re.compile(r'\b[А-Яа-яЁё]+\b')
    censored_text = pattern.sub(censor_match, value)
    return censored_text