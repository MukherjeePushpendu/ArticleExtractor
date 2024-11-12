import pandas as pd
import requests
from bs4 import BeautifulSoup
import os
import nltk

# Download necessary NLTK data
nltk.download('punkt_tab')

# Load URLs from Input.xlsx
input_df = pd.read_excel('Input.xlsx')

# Create a directory to save the text files if it doesn't exist
os.makedirs('extracted_articles', exist_ok=True)

# Loop through each URL in the input file
for idx, row in input_df.iterrows():
    url_id = row['URL_ID']
    url = row['URL']

    try:
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract title and main article content
        title = soup.find('h1').get_text(strip=True)  # Adjust selector if necessary
        article_body = ' '.join([p.get_text(strip=True) for p in soup.find_all('p')])

        # Save the extracted text to a file
        with open(f'extracted_articles/{url_id}.txt', 'w', encoding='utf-8') as file:
            file.write(f"{title}\n{article_body}")

        print(f"Article {url_id} extracted successfully.")

    except Exception as e:
        print(f"Error extracting article {url_id}: {e}")

import nltk
from nltk.corpus import stopwords
from textstat import syllable_count
import re
import os
import pandas as pd

# Load positive and negative dictionaries
positive_words = set(open('MasterDictionary/positive-words.txt').read().split())
negative_words = set(open('MasterDictionary/negative-words.txt').read().split())
stop_words = set(stopwords.words('english'))

# Initialize output dataframe
output_data = []

# Loop through each text file in extracted_articles
for filename in os.listdir('extracted_articles'):
    if filename.endswith('.txt'):
        with open(f'extracted_articles/{filename}', 'r', encoding='utf-8') as file:
            text = file.read()

        # Tokenize and clean text
        words = nltk.word_tokenize(text.lower())
        clean_words = [word for word in words if word.isalpha() and word not in stop_words]

        # Calculate variables
        positive_score = sum(1 for word in clean_words if word in positive_words)
        negative_score = sum(1 for word in clean_words if word in negative_words)
        polarity_score = (positive_score - negative_score) / ((positive_score + negative_score) + 0.000001)
        subjectivity_score = (positive_score + negative_score) / (len(clean_words) + 0.000001)

        # Sentence and word-level metrics
        sentences = nltk.sent_tokenize(text)
        avg_sentence_length = len(clean_words) / len(sentences)
        complex_words = [word for word in clean_words if syllable_count(word) > 2]
        percentage_complex_words = len(complex_words) / len(clean_words)
        fog_index = 0.4 * (avg_sentence_length + percentage_complex_words)

        # Other metrics
        word_count = len(clean_words)
        avg_word_length = sum(len(word) for word in clean_words) / word_count
        syllables_per_word = sum(syllable_count(word) for word in clean_words) / word_count
        personal_pronouns = len(re.findall(r'\b(I|we|my|ours|us)\b', text, re.I))

        # Save results
        output_data.append([
            filename.split('.')[0], positive_score, negative_score, polarity_score,
            subjectivity_score, avg_sentence_length, percentage_complex_words, fog_index,
            len(sentences), len(complex_words), word_count, syllables_per_word,
            personal_pronouns, avg_word_length
        ])

# Save output to an Excel file
output_df = pd.DataFrame(output_data, columns=[
    'URL_ID', 'Positive Score', 'Negative Score', 'Polarity Score', 'Subjectivity Score',
    'Avg Sentence Length', 'Percentage Complex Words', 'Fog Index',
    'Avg Number of Words Per Sentence', 'Complex Word Count', 'Word Count',
    'Syllable per Word', 'Personal Pronouns', 'Avg Word Length'
])
output_df.to_excel('Output Data Structure.xlsx', index=False)

import nltk
nltk.download('punkt')
nltk.download('stopwords')

positive_dict = '/path/to/your/directory/MasterDictionary/positive-words.txt'
negative_dict = '/path/to/your/directory/MasterDictionary/negative-words.txt'
