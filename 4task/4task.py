import spacy
import nltk
from nltk.corpus import stopwords
from collections import defaultdict
from bs4 import BeautifulSoup
import numpy as np
import os

    


class Tf_Idf:

    if not os.path.exists('lemmas'):
        os.makedirs('lemmas')

    if not os.path.exists('tokens'):
        os.makedirs('tokens')
    
    
    def __init__(self, path):
        self.path = path
        self.count = 101
        self.nlp = spacy.load('ru_core_news_sm')

        nltk.download('stopwords')
        self.nltk_stopwords = stopwords.words("russian")

        self.docs_tokens = defaultdict(dict)
        self.docs_lemmas = defaultdict(dict)

        self.token_in_docs = defaultdict(int)
        self.lemmas_in_docs = defaultdict(int)

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
    def write_tokens(path, docs_tokens, tokens_in_docs):
        for doc_id in docs_tokens:
            with open(f"{path}/tf-idf_{doc_id}.txt", 'w', encoding='utf-8') as file:
                for tokens in docs_tokens[doc_id]:
                    tf = docs_tokens[doc_id][tokens] / len(docs_tokens[doc_id])
                    idf = np.log10(len(tokens_in_docs) / tokens_in_docs[tokens])
                    file.write(f"{tokens} {idf} {tf * idf} \n")

    @staticmethod
    def write_lemmas(path, docs_lemmas, lemmas_in_docs):
        for doc_id in docs_lemmas:
            with open(f"{path}/tf-idf_{doc_id}.txt", 'w', encoding='utf-8') as file:
                for lemmas in docs_lemmas[doc_id]:
                    tf = docs_lemmas[doc_id][lemmas] / len(docs_lemmas[doc_id])
                    idf = np.log10(len(lemmas_in_docs) / lemmas_in_docs[lemmas])
                    file.write(f"{lemmas} {idf} {tf * idf}\n")

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

    @staticmethod
    def check_contains_docs(item, type_item):
        if item.__contains__(type_item):
            item[type_item] += 1
        else:
            item[type_item] = 1

        return item

    def tokenization(self, html_text, doc_id):
        tokens = self.nlp(str(html_text))
        tokens_use = []
        lemmas_use = []
        self.docs_tokens[doc_id] = dict()
        self.docs_lemmas[doc_id] = dict()

        for token in tokens:
            if self.check_for_rules_token(token):

                self.docs_lemmas[doc_id] = self.check_contains_docs(self.docs_lemmas[doc_id], token.lemma_)

                self.docs_tokens[doc_id] = self.check_contains_docs(self.docs_tokens[doc_id], token.text)

                if token.text not in tokens_use:
                    self.token_in_docs = self.check_contains_docs(self.token_in_docs, token.text)
                    tokens_use.append(token.text)

                if token.lemma_ not in lemmas_use:
                    self.lemmas_in_docs = self.check_contains_docs(self.lemmas_in_docs, token.lemma_)
                    lemmas_use.append(token.lemma_)

    def start(self):
        for i in range(1, self.count):
            path = f'{self.path}/{i}.html'
            html_text = self.read_file(path, self._get_html_text)

            self.tokenization(html_text, i)

            print(f"файл готов - {i}")

        self.write_lemmas('lemmas', self.docs_lemmas, self.lemmas_in_docs)

        print(f"lemmas write")

        self.write_tokens('tokens', self.docs_tokens, self.token_in_docs)

        print(f"tokens write")


if __name__ == '__main__':
    lemma_tokenizer = Tf_Idf('../2task/html')

    lemma_tokenizer.start()