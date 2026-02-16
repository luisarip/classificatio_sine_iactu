import pandas as pd
import re

def extract_sentences_from_tsv(file_path):
    """
    Parses a TSV where the first column contains tokens and the 10th column 
    contains 'EndOfSentence' markers or comments.
    """
    df = pd.read_csv(file_path, sep='\t', header=None)

    # ensure header is set
    if df.columns[0] == 0 and df.iloc[0, 0] == "TOKEN":
        df.columns = df.iloc[0]
        df = df[1:]

    sentences = []
    current_sentence = []

    for _, row in df.iterrows():
        token = str(row.iloc[0])
        misc = str(row.iloc[9])

        if token.startswith('#'):
            if current_sentence:
                sentences.append(" ".join(current_sentence))
                current_sentence = []
            continue

        current_sentence.append(token.replace('\n', ''))

        if 'EndOfSentence' in misc:
            sentences.append(" ".join(current_sentence))
            current_sentence = []

    if current_sentence:
        sentences.append(" ".join(current_sentence))
    
    return sentences