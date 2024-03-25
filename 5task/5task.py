import os
import numpy as np

import spacy


class VectorizeSearch:
    def __init__(self, path_to_lemmas, path_to_tokens, path_tf_idf_lemmas):
        self.nlp = spacy.load("ru_core_news_sm")
        self.path_to_lemmas = path_to_lemmas
        self.path_to_tokens = path_to_tokens
        self.path_tf_idf_lemmas = path_tf_idf_lemmas
        self.lemmas = []
        self.pages_dict = {}

    @staticmethod
    def read_lemmas(path_to_lemmas):
        lemmas = []
        with open(path_to_lemmas, 'r', encoding='utf-8') as file:
            for line in file:
                lemmas_split = line.split(" ")
                lemmas.append(lemmas_split[0])

        return lemmas

    @staticmethod
    def read_tf_idf(path_lemmas_tf_idf, lemmas, nlp):
        pages_dict = {}
        for file in os.listdir(path_lemmas_tf_idf):
            with open(f"{path_lemmas_tf_idf}/{file}", 'r', encoding="utf-8") as f:
                page_num = file.split("_")[1].strip(".txt")
                pages_dict[page_num] = [0] * len(lemmas)

                for line in f:
                    line_split = line.split(" ")
                    word = line_split[0]
                    try:
                        pages_dict[page_num][lemmas.index(nlp(word)[0].lemma_)] = float(line_split[2])
                    except Exception as e:
                        pass
                print(pages_dict[page_num])
            print(f'ready ${file}')
        return pages_dict

    @staticmethod
    def words_vectorize(lemmas, words, nlp):
        word_weight = len(words) / len(lemmas)
        word_vector = [0] * len(lemmas)

        for word in words:
            try:
                word_vector[lemmas.index(nlp(word)[0].lemma_)] = word_weight
            except Exception as e:
                pass

        return word_vector

    @staticmethod
    def count_coef_otiai(page_vector, words_vector):
        scalar_vectors = np.dot(page_vector, words_vector)

        coef_otiai = scalar_vectors / np.sqrt(np.sum(words_vector) * np.sum(page_vector))

        return coef_otiai

    def vectorize_pages(self):
        self.lemmas = self.read_lemmas(self.path_to_lemmas)
        self.pages_dict = self.read_tf_idf(self.path_tf_idf_lemmas, self.lemmas, self.nlp)

    def search(self, request):
        words_vector = self.words_vectorize(self.lemmas, request.split(), self.nlp)

        result_search = []

        for key in self.pages_dict:
            page_vector = self.pages_dict.get(key)

            coef_otiai = self.count_coef_otiai(page_vector, words_vector)

            if not np.isnan(coef_otiai):
                result_search.append((key, coef_otiai))

        return sorted(result_search, key=lambda x: x[1], reverse=True)


if __name__ == '__main__':
    vectorize_search = VectorizeSearch('../2task/lemmas.txt', '../2task/tokens.txt', '../4task/lemmas')

    vectorize_search.vectorize_pages()

    while True:
        input_request = input("Введите запрос: ")

        result = vectorize_search.search(input_request)

        print(result)