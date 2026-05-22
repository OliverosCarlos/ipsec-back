import re
from django import template
from num2words import num2words

register = template.Library()


@register.filter
def format_phone(value):
    """
    Formatea un número de teléfono a (XXX) XXX-XXXX.
    Acepta 10 dígitos con o sin caracteres separadores.
    Ejemplos:
        3111605000      → (311) 160-5000
        +523111605000   → (311) 160-5000
        311-160-5000    → (311) 160-5000
    """
    if not value:
        return value
    digits = re.sub(r'\D', '', str(value))
    # Elimina prefijo de país (52 para México) si el número tiene más de 10 dígitos
    if len(digits) > 10:
        digits = digits[-10:]
    if len(digits) == 10:
        return f'({digits[:3]}) {digits[3:6]}-{digits[6:]}'
    return value


@register.filter
def amount_to_words(value, currency='MXN'):
    """
    Convierte un monto numérico a palabras en español.
    Ejemplo: 23432.00 → 'VEINTITRÉS MIL CUATROCIENTOS TREINTA Y DOS PESOS 00/100 M.N. (MXN $23,432.00)'
    """
    try:
        amount = float(value)
    except (TypeError, ValueError):
        return value

    enteros = int(amount)
    centavos = round((amount - enteros) * 100)

    palabras = num2words(enteros, lang='es').upper()
    return f'{palabras} PESOS {centavos:02d}/100 M.N. ({currency} ${amount:,.2f})'
