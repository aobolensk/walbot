import re

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

# Reference: https://gist.github.com/Alex-Just/e86110836f3f93fe7932290526529cd1#gistcomment-3208085
UNICODE_EMOJI_REGEX = re.compile(
    "["
    "\U0001F1E0-\U0001F1FF"  # flags (iOS)
    "\U0001F300-\U0001F5FF"  # symbols & pictographs
    "\U0001F600-\U0001F64F"  # emoticons
    "\U0001F680-\U0001F6FF"  # transport & map symbols
    "\U0001F700-\U0001F77F"  # alchemical symbols
    "\U0001F780-\U0001F7FF"  # Geometric Shapes Extended
    "\U0001F800-\U0001F8FF"  # Supplemental Arrows-C
    "\U0001F900-\U0001F9FF"  # Supplemental Symbols and Pictographs
    "\U0001FA00-\U0001FA6F"  # Chess Symbols
    "\U0001FA70-\U0001FAFF"  # Symbols and Pictographs Extended-A
    "\U00002702-\U000027B0"  # Dingbats
    "\U000024C2-\U0001F251"
    "]"
)
