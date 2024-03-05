import spacy
from collections import defaultdict
from nltk.corpus import stopwords
from bs4 import BeautifulSoup

nlp = spacy.load("ru_core_news_sm")
docs_ids = set()
indexes = defaultdict(set)
stopwords = stopwords.words("russian")
dict_index = {}


def write_index():
    with open('inverted_index.txt', 'a', encoding='utf-8') as file:
        result_content = ''
        for key, value in dict_index.items():
            result_content += f'{key} '
            for index in value:
                result_content += f'{index} '
            result_content += f'\n'
        file.write(result_content)

def generate_indexes():
    for i in range(0, 100):
        docs_ids.add(i)
        with open("../2task/html/" + str(i) + ".html", encoding='utf-8') as file:
            html = BeautifulSoup(file, features="html.parser")
            process(nlp(str(html.get_text(" ").lower().strip())), i)
    write_index()

def check_for_russia_letter(word):
    alphabet = ["а", "б", "в", "г", "д", "е", "ё", "ж", "з", "и", "й", "к", "л", "м", "н", "о", "п", "р", "с",
                "т",
                "у", "ф", "х", "ц", "ч", "ш", "щ", "ъ", "ы", "ь", "э", "ю", "я"]

    for letter in word:
        if letter not in alphabet:
            return False
    return True

def check_for_rules_token(token):
    if token.text not in stopwords \
            and token.is_alpha \
            and not token.like_num \
            and not token.is_punct \
            and check_for_russia_letter(token.text):
        return True

    return False

def process(doc, doc_id):
    for item in doc:
        if check_for_rules_token(item):
            indexes[item.lemma_].add(doc_id)

            if item.text not in dict_index:
                dict_index[item.text] = []

            if item.text in dict_index and doc_id not in dict_index[item.text]:
                dict_index[item.text].append(doc_id)

def evaluate_query(query):
    if query[1] == 'NOT':
        return docs_ids - indexes[query[0]]
    elif query[1] == 'AND':
        return indexes[query[0]].intersection(indexes[query[2]])
    elif query[1] == 'OR':
        return indexes[query[0]].union(indexes[query[2]])
    else:
        print(f"Invalid query format: {query}")
        return set()

def parse_query(query):
    query = query.replace(' ', '')
    queries = []
    i = 0
    while i < len(query):
        if query[i] == '(':
            j = i + 1
            depth = 1
            while depth > 0:
                j += 1
                if query[j] == '(':
                    depth += 1
                elif query[j] == ')':
                    depth -= 1
            q = query[i+1:j]
            operator = None
            if 'AND' in q:
                operator = 'AND'
                parts = q.split('AND')
            elif 'OR' in q:
                operator = 'OR'
                parts = q.split('OR')
            elif 'NOT' in q:
                operator = 'NOT'
                parts = q.split('NOT')
            if operator is None:
                print(f"Invalid query format: {query[i:j+1]}")
                return []
            if len(parts) == 2:
                queries.append((parts[0], operator, parts[1]))
            else:
                queries.append((parts[0], operator, ''))
            i = j + 1
        else:
            i += 1
    return queries

def main():
    generate_indexes()
    query = input("Enter your query: ")
    queries = parse_query(query)
    result = set()
    for i, q in enumerate(queries):
        if i == 0:
            result = evaluate_query(q)
        else:
            result = result.union(evaluate_query(q))
    print(f"Files matching query {query}: {result}")

if __name__ == '__main__':
    main()
