
import pandas as pd
import re

# ===================================================================
# Paths (edit if needed)
# ===================================================================
RAW_PATH = r'C:\Users\Suva\Downloads\phone_aspect_reviews_817\phone_aspect_reviews_817.csv'
OUTPUT_PATH = r'C:\Users\Suva\Downloads\phone_aspect_reviews_817\phone_aspect_reviews_cleaned.csv'

# ===================================================================
# 0) Load data
# ===================================================================
df = pd.read_csv(RAW_PATH)
if 'review_text' not in df.columns:
    raise ValueError("Input CSV must contain a 'review_text' column.")
df = df.drop_duplicates(subset=['review_text']).copy()
df['review_text'] = df['review_text'].astype(str).str.strip()

# ===================================================================
# 1) Remove URLs
# ===================================================================
URL_RE = re.compile(r'https?://\S+|www\.\S+')
def remove_urls(text: str) -> str:
    return URL_RE.sub('', text).strip()

df['review_text'] = df['review_text'].apply(remove_urls)
df = df[df['review_text'].str.len() > 0].copy()

# ===================================================================
# 2) Fix mis-encoded chars / curly quotes / strip non-ASCII
# ===================================================================
replacements = {
    'â€™': "'", 'â€˜': "'", 'â€œ': '"', 'â€': '"',
    'â€“': '-', 'â€”': '-', 'â€¦': '...',
    '’': "'", '‘': "'", '“': '"', '”': '"',
    '–': '-', '—': '-', '…': '...'
}
def fix_text(text: str) -> str:
    s = str(text)
    for wrong, correct in replacements.items():
        s = s.replace(wrong, correct)
    # remove garbled emoji codes (e.g., ðŸ…)
    s = re.sub(r'ðŸ\S*', '', s)
    # strip any remaining non-ASCII characters
    s = re.sub(r'[^\x00-\x7F]+', '', s)
    # collapse whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    return s

df['review_text'] = df['review_text'].apply(fix_text)
df = df[df['review_text'].str.len() > 0].copy()

# ===================================================================
# 3) Likely-English filter (lightweight heuristic)
# ===================================================================
common_words = [' the ',' and ',' is ',' it ',' this ',' that ',' to ',' for ',' i ',
                ' in ',' on ',' with ',' you ',' your ',' are ',' be ',' have ',' has ']
def is_english(text: str) -> bool:
    t = ' ' + text.lower() + ' '
    return any(w in t for w in common_words)

df = df[df['review_text'].apply(is_english)].copy()
# also require a minimum token count
df = df[df['review_text'].str.split().str.len() >= 5].copy()

# ===================================================================
# 4) Keep only reviews that mention phone brands/features
# ===================================================================
brands = ['phone','smartphone','iphone','samsung','galaxy','pixel','moto','xiaomi',
          'oneplus','sony','huawei','nokia','oppo','vivo','asus','lenovo','motorola','android','ios']
features = ['battery','camera','screen','display','performance','processor','storage',
            'ram','memory','charger','charging','touch','fingerprint','speaker','sound',
            'microphone','wifi','bluetooth','network','signal','lag','software',
            'update','call','5g','resolution','refresh','heat','heating','app']
BRAND_OR_FEATURE_RE = re.compile('|'.join(re.escape(k) for k in brands + features), re.IGNORECASE)

df = df[df['review_text'].apply(lambda x: bool(BRAND_OR_FEATURE_RE.search(x)))].copy()

# ===================================================================
# 5) Remove question sentences inside multi-sentence reviews
# ===================================================================
QUESTION_WORDS = (
    'what', 'why', 'how', 'when', 'where', 'who', 'whom', 'whose', 'which',
    'can', 'could', 'would', 'should', 'do', 'does', 'did',
    'is', 'are', 'am', 'was', 'were', 'will', 'shall', 'may', 'might'
)
# split sentences on ., !, ? followed by whitespace
SENT_SPLIT_RE = re.compile(r'(?<=[.!?])\s+')

def looks_like_question(sent: str) -> bool:
    s = sent.strip()
    if not s:
        return False
    lower = s.lower().lstrip('"\''"“”‘’()[]{}<>-–— ").strip()
    # ends with ? or starts with a common question word
    if s.endswith('?'):
        return True
    first_token = lower.split(' ', 1)[0] if lower else ''
    if first_token in QUESTION_WORDS:
        return True
    # short interrogatives
    if lower.startswith(('any ', 'anyone ', 'anybody ', 'someone ', 'does anyone', 'can anyone')):
        return True
    # has a '?' anywhere (e.g., "battery? terrible.")
    if '?' in s:
        return True
    return False

def remove_question_sentences(text: str) -> str:
    sentences = SENT_SPLIT_RE.split(text)
    kept = [s.strip() for s in sentences if s.strip() and not looks_like_question(s)]
    cleaned = ' '.join(kept)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned

df['review_text'] = df['review_text'].apply(remove_question_sentences)
df = df[df['review_text'].str.len() > 0].copy()

# ===================================================================
# 6) Extra noise cleanup for the remaining mess
#     - leading '>' quote markers or '- >'
#     - numbered list prefixes like "3) ", "1.", "(2) -"
#     - ASCII emoticons like ':)', ':(', ':D', 'XD', '<3'
#     - weird headers like "There *are* NOS --"
#     - repeated dashes/punctuation, leading bullets
# ===================================================================
ASCII_EMOJI_RE         = re.compile(r'(?<!\w)(?:[:;=8xX][-~]?[)(DPp/\\]|<3|:\)|:\(|:D|:P|XD)(?!\w)')
LEADING_QUOTE_ARROW_RE = re.compile(r'^\s*(?:>\s*)+|-\s*>')
NUMBERED_PREFIX_RE     = re.compile(r'^\s*(?:\(?\d{1,3}\)?[.)-]\s*)+')
THERE_ARE_NOS_RE       = re.compile(r'^\s*there\s*\*?are\*?\s+[A-Z]{2,}\b\s*(?:--|—|-)\s*', re.IGNORECASE)
BULLET_PREFIX_RE       = re.compile(r'^\s*[*•\-–—]+\s+')

def clean_line_noise(text: str) -> str:
    s = str(text)

    # strip leading bullets first (e.g., "- something", "• item")
    s = BULLET_PREFIX_RE.sub('', s)

    # Remove leading quote/arrow junk and enumerations
    s = LEADING_QUOTE_ARROW_RE.sub('', s)
    s = NUMBERED_PREFIX_RE.sub('', s)

    # "There *are* NOS --" or similar banner-ish headers
    s = THERE_ARE_NOS_RE.sub('', s)

    # Strip ASCII emoticons
    s = ASCII_EMOJI_RE.sub('', s)

    # Normalize arrows/dashes and collapse repeats
    s = re.sub(r'\s*-\s*>', ' ', s)     # "- >" -> space
    s = re.sub(r'--+', '-', s)          # "--", "---" -> "-"
    s = re.sub(r'\s*–\s*', '-', s)      # en-dash normalize
    s = re.sub(r'\s*—\s*', '-', s)      # em-dash normalize
    s = re.sub(r'([!?.,-])\1{1,}', r'\1', s)  # "!!", "??", "..." -> single

    # Trim stray quotes/pipes and extra spaces
    s = s.strip(' "\'|>')
    s = re.sub(r'\s+', ' ', s).strip()
    return s

df['review_text'] = df['review_text'].apply(clean_line_noise)
df = df[df['review_text'].str.len() > 0].copy()

# (Optional) enforce min length again after stripping junk
df = df[df['review_text'].str.split().str.len() >= 5].copy()

# ===================================================================
# Save
# ===================================================================
df.to_csv(OUTPUT_PATH, index=False)

print("Cleaning complete.")
print("Rows remaining:", len(df))
print("Saved to:", OUTPUT_PATH)