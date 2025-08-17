import pandas as pd
import re

# Load the raw data
df = pd.read_csv(r'C:\Users\Suva\Documents\MSC_DS_AI\ML\Project\phone_reviews_new.csv')
df = df.drop_duplicates(subset=['review_text'])  # remove duplicate reviews
df['review_text'] = df['review_text'].astype(str).str.strip()

# 1. Remove URLs from review_text
url_pattern = re.compile(r'https?://\S+|www\.\S+')
def remove_urls(text):
    return url_pattern.sub('', text).strip()

df['review_text'] = df['review_text'].apply(remove_urls)
df = df[df['review_text'].str.len() > 0]

# 2. Fix mis‑encoded characters and curly quotes, then strip any remaining non‑ASCII
replacements = {
    'â€™': "'", 'â€˜': "'", 'â€œ': '"', 'â€': '"',
    'â€“': '-', 'â€”': '-', 'â€¦': '...',
    '’': "'", '‘': "'", '“': '"', '”': '"',
    '–': '-', '—': '-', '…': '...'
}
def fix_text(text):
    for wrong, correct in replacements.items():
        text = text.replace(wrong, correct)
    # remove garbled emoji codes (e.g. ðŸ…)
    text = re.sub(r'ðŸ\S*', '', text)
    # strip any remaining non‑ASCII characters
    text = re.sub(r'[^\x00-\x7F]+', '', text)
    return text

df['review_text'] = df['review_text'].apply(fix_text)
df = df[df['review_text'].str.len() > 0]

# 3. (Optional) keep only likely English reviews and those mentioning phone features/brands
common_words = [' the ',' and ',' is ',' it ',' this ',' that ',' to ',' for ',' i ',
                ' in ',' on ',' with ',' you ',' your ',' are ',' be ',' have ',' has ']
def is_english(text):
    t = ' ' + text.lower() + ' '
    return any(w in t for w in common_words)

df = df[df['review_text'].apply(is_english)]
df = df[df['review_text'].str.split().str.len() >= 5]

brands = ['phone','smartphone','iphone','samsung','galaxy','pixel','moto','xiaomi',
          'oneplus','sony','huawei','nokia','oppo','vivo','asus','lenovo','motorola','android','ios']
features = ['battery','camera','screen','display','performance','processor','storage',
            'ram','memory','charger','charging','touch','fingerprint','speaker','sound',
            'microphone','wifi','bluetooth','network','signal','lag','software',
            'update','call','5g','resolution','refresh','heat','heating','app']
pattern = re.compile('|'.join(re.escape(k) for k in brands+features), re.IGNORECASE)
df = df[df['review_text'].apply(lambda x: bool(pattern.search(x)))]

# Save the cleaned output
df.to_csv(r'C:\Users\Suva\Documents\MSC_DS_AI\ML\Project\phone_reviews_cleaned_no_urls.csv', index=False)
