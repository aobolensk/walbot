from src import const

alphabet = "🇦🇧🇨🇩🇪🇫🇬🇭🇮🇯🇰🇱🇲🇳🇴🇵🇶🇷🇸🇹🇺🇻🇼🇽🇾🇿"

text_to_emoji = {
    'a': '🇦',
    'b': '🇧',
    'c': '🇨',
    'd': '🇩',
    'e': '🇪',
    'f': '🇫',
    'g': '🇬',
    'h': '🇭',
    'i': '🇮',
    'j': '🇯',
    'k': '🇰',
    'l': '🇱',
    'm': '🇲',
    'n': '🇳',
    'o': '🇴',
    'p': '🇵',
    'q': '🇶',
    'r': '🇷',
    's': '🇸',
    't': '🇹',
    'u': '🇺',
    'v': '🇻',
    'w': '🇼',
    'x': '🇽',
    'y': '🇾',
    'z': '🇿',
    '0': '0️⃣',
    '1': '1️⃣',
    '2': '2️⃣',
    '3': '3️⃣',
    '4': '4️⃣',
    '5': '5️⃣',
    '6': '6️⃣',
    '7': '7️⃣',
    '8': '8️⃣',
    '9': '9️⃣',
    '#': '#️⃣',
    '*': '*️⃣',
    '!': '❗',
    '?': '❓',
    'а': '🇦',
    'б': '🇧',
    'в': '🇻',
    'г': '🇬',
    'д': '🇩',
    'е': '🇪',
    'ё': '🇪',
    'ж': '🇿 🇭',
    'з': '🇿',
    'и': '🇮',
    'й': '🇮',
    'к': '🇰',
    'л': '🇱',
    'м': '🇲',
    'н': '🇳',
    'о': '🇴',
    'п': '🇵',
    'р': '🇷',
    'с': '🇸',
    'т': '🇹',
    'у': '🇺',
    'ф': '🇫',
    'х': '🇰 🇭',
    'ц': '🇹 🇸',
    'ч': '🇨 🇭',
    'ш': '🇸 🇭',
    'щ': '🇸 🇭 🇨 🇭',
    'ъ': '',
    'ы': '🇾',
    'ь': '',
    'э': '🇪',
    'ю': '🇮 🇺',
    'я': '🇮 🇦',
}

emoji_to_text = {
    '🇦': 'a',
    '🇧': 'b',
    '🇨': 'c',
    '🇩': 'd',
    '🇪': 'e',
    '🇫': 'f',
    '🇬': 'g',
    '🇭': 'h',
    '🇮': 'i',
    '🇯': 'j',
    '🇰': 'k',
    '🇱': 'l',
    '🇲': 'm',
    '🇳': 'n',
    '🇴': 'o',
    '🇵': 'p',
    '🇶': 'q',
    '🇷': 'r',
    '🇸': 's',
    '🇹': 't',
    '🇺': 'u',
    '🇻': 'v',
    '🇼': 'w',
    '🇽': 'x',
    '🇾': 'y',
    '🇿': 'z',
    '0️⃣': '0',
    '1️⃣': '1',
    '2️⃣': '2',
    '3️⃣': '3',
    '4️⃣': '4',
    '5️⃣': '5',
    '6️⃣': '6',
    '7️⃣': '7',
    '8️⃣': '8',
    '9️⃣': '9',
    '#️⃣': '#',
    '*️⃣': '*',
    '❗': '!',
    '❓': '?',
}


def get_clock_emoji(time: str):
    r = const.TIME_24H_REGEX.match(time)
    if r is None:
        return
    hours, minutes = (int(x) for x in r.groups())
    if minutes < 15:
        minutes = 0
    elif 15 <= minutes < 45:
        minutes = 30
    else:  # 45 <= minutes < 60
        minutes = 0
        hours += 1
    while hours > 12:
        hours -= 12
    while hours <= 0:
        hours += 12
    return f":clock{hours}{minutes if minutes > 0 else ''}:"
