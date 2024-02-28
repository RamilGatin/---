import spacy
import nltk
from nltk.corpus import stopwords
from collections import defaultdict
from bs4 import BeautifulSoup


class Lemma_Tokenizer:
    def __init__(self, path):
        self.path = path
        self.count = 101
        self.nlp = spacy.load('ru_core_news_sm')

        nltk.download('stopwords')
        self.nltk_stopwords = stopwords.words("russian")

        self.lemmas = defaultdict(set)
        self.tokens = set()

    @staticmethod
    def _get_html_text(file):
        bs4 = BeautifulSoup(file, features='html.parser')

        return bs4.get_text(" ", strip=True).lower()

    @staticmethod
    def read_file(path, _get_html_text):
        with open(path, 'r', encoding='utf-8') as file:
            get_text = _get_html_text(file)

        return get_text

    @staticmethod
    def write_tokens(path, tokens):
        with open(path, 'w', encoding='utf-8') as file:
            file.write("\n".join(list(tokens)))

    @staticmethod
    def write_lemmas(path, lemmas):
        lemma_list = []

        for key, values in lemmas.items():
            lemma_list.append(f"{key} {' '.join(list(values))}")

        with open(path, 'w', encoding='utf-8') as file:
            file.write("\n".join(lemma_list))

    @staticmethod
    def check_for_russia_letter(word):
        alphabet = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с",
                    "т",
                    "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]

        for letter in word:
            if letter not in alphabet:
                return False

        return True

    def check_for_rules_token(self, token):
        if token.text not in self.nltk_stopwords \
                and token.is_alpha \
                and not token.like_num \
                and not token.is_punct \
                and self.check_for_russia_letter(token.text):
            return True

        return False

    def tokenization(self, html_text):
        tokens = self.nlp(str(html_text))

        for token in tokens:
            if self.check_for_rules_token(token):
                self.tokens.add(token.text)
                self.lemmas[token.lemma_].add(token.text)

    def start(self):
        for i in range(self.count):
            path = f'{self.path}/{i}.html'
            html_text = self.read_file(path, self._get_html_text)

            self.tokenization(html_text)

            print(f'ready file {i}.html')

        self.write_tokens('tokens.txt', self.tokens)
        self.write_lemmas('lemmas.txt', self.lemmas)


if __name__ == '__main__':
    lemma_tokenizer = Lemma_Tokenizer('html')

    lemma_tokenizer.start()