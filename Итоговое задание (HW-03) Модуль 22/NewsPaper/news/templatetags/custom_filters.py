from django import template
import re

register = template.Library()

BAD_WORDS = {'слово'}

@register.filter(name='censor_words')
def censor_words(value):
    if not isinstance(value, str):
        return value

    def censor_match(match):
        word = match.group()
        if len(word) > 1 and (word[0].isalpha() and word[0].lower() == word[0] or word[0].isupper()):
            if word.lower() in BAD_WORDS:
                return word[0] + '*' * (len(word) - 1)
        return word

    pattern = re.compile(r'\b[А-Яа-яЁё]+\b')
    censored_text = pattern.sub(censor_match, value)
    return censored_text

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)