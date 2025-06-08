from config import keys
import requests
import json

class APIException(Exception):
    pass 

class CryptoConverter:
    @staticmethod
    def get_price(quote: str, base: str, amount: str):
        if quote == base:
            raise APIException(f"Для конвертации введены одинаковые валюты {base}!\nЗначение валют не должно совпадать.")
        try:
            quote_ticker = keys[quote]
        except KeyError:
            raise APIException(f'Ошибка в написании {quote}.\nВоспользуйтесь командой /values для просмотра допустимых валют.')
        try:
            base_ticker = keys[base]
        except KeyError:
            raise APIException(f'Ошибка в написании {base}.\nВоспользуйтесь командой /values для просмотра допустимых валют.')
        try:
            amount = float(amount)
        except ValueError:
            raise APIException(f'Введное значение не является числовым - "{amount}".')
        
        r = requests.get(f"https://min-api.cryptocompare.com/data/price?fsym={quote_ticker}&tsyms={base_ticker}")
        total_base = json.loads(r.content)[keys[base]]
        return total_base