from simalign import SentenceAligner
import re
import pandas as pd

def align_latin(
    tsv_output: pd.DataFrame,
    entities_df: pd.DataFrame,
    token_col: str = "TOKEN",
    misc_col: str = "MISC",
    sentence_marker: str = "EndOfSentence"
) -> pd.Series:
    """
    Align entity predictions to TSV tokens and return BIO tag column.

    Parameters
    ----------
    tsv_output : pd.DataFrame
        Original TSV dataframe with tokens.
    entities_df : pd.DataFrame
        DataFrame with column 'entities' (one row per sentence).
    token_col : str
        Column name for tokens.
    misc_col : str
        Column containing sentence boundary marker.
    sentence_marker : str
        Marker indicating end of sentence.

    Returns
    -------
    pd.Series
        BIO tags aligned to TSV rows.
    """

    df = tsv_output.reset_index(drop=True)
    bio_tags = ["O"] * len(df)

    # --- build sentence ranges ---
    sentence_ranges = []
    start = 0

    for i, misc in enumerate(df[misc_col].fillna("")):
        if sentence_marker in str(misc):
            sentence_ranges.append((start, i))
            start = i + 1

    if start < len(df):
        sentence_ranges.append((start, len(df) - 1))

    if len(sentence_ranges) != len(entities_df):
        print("⚠️ Sentence count mismatch:", len(sentence_ranges), "TSV vs", len(entities_df), "entity rows")

    # --- helper matcher ---
    def match_entity(tokens, entity_tokens):
        n = len(entity_tokens)
        for i in range(len(tokens) - n + 1):
            if tokens[i:i+n] == entity_tokens:
                return i
        return None

    # --- alignment loop ---
    for sent_idx, ((start, end), row) in enumerate(
        zip(sentence_ranges, entities_df["entities"])
    ):
        sent_tokens = df.loc[start:end, token_col].astype(str).tolist()

        if not isinstance(row, dict) or "entities" not in row:
            continue

        for ent_type, ent_list in row["entities"].items():
            for ent in ent_list:
                text = ent["text"]
                ent_tokens = text.split()

                match_pos = match_entity(sent_tokens, ent_tokens)
                if match_pos is None:
                    print(f"❌ Not aligned | sentence {sent_idx} | entity '{text}'")
                    continue

                for i, token in enumerate(ent_tokens):
                    absolute_idx = start + match_pos + i

                    # lowercase rule
                    if token.islower():
                        continue

                    prefix = "B" if i == 0 else "I"
                    bio_tags[absolute_idx] = f"{prefix}-{ent_type}"

    return pd.Series(bio_tags, index=tsv_output.index)

def align_english(df_results, tsv_df, column_name='bio_tag'):
    """
    Aligns entities from English to Latin and saves BIO tags in the specified column.
    
    Parameters:
    -----------
    df_results : pd.DataFrame
        DataFrame containing 'sentences_la', 'sentences_en', and 'entities' columns
    tsv_df : pd.DataFrame
        DataFrame with 'TOKEN' column where BIO tags will be added
    column_name : str
        Name of the column to store BIO tags (default: 'bio_tag')
    
    Returns:
    --------
    pd.DataFrame
        The tsv_df with the new BIO tag column added
    """
    
    # Initialize aligner
    aligner = SentenceAligner(
        model="UGARIT/grc-alignment",
        token_type="bpe",
        matching_methods="i"
    )
    
    def pad_punctuation(text):
        """Adds a space before punctuation symbols"""
        if isinstance(text, str):
            return re.sub(r'([.,!?;:])', r' \1', text)
        return text
    
    # Apply padding to English sentences
    df_results["sentences_en"] = df_results["sentences_en"].apply(pad_punctuation)
    
    # Robust fix: if some English sentence is missing, replace with Latin one
    df_results["sentences_en"] = df_results.apply(
        lambda row: row["sentences_la"]
        if not isinstance(row["sentences_en"], str) or not row["sentences_en"].strip()
        else row["sentences_en"],
        axis=1
    )

    # Step 1: Get alignments
    mapping = []
    for idx, row in df_results.iterrows():
        la = row["sentences_la"]
        en = row["sentences_en"]
        string_aligned = aligner.get_word_aligns(la, en).get("itermax", [])
        mapping.append(string_aligned)
    df_results["alignment"] = mapping
    
    # Step 2: Map entities from English to Latin
    results = []
    for _, row in df_results.iterrows():
        en_tokens = row["sentences_en"].split()
        la_tokens = row["sentences_la"].split()
        
        # Create a mapping: English Index -> List of Latin Indices
        align_map = {}
        for la_idx, en_idx in row["alignment"]:
            align_map.setdefault(en_idx, []).append(la_idx)
        
        row_mappings = []
        entities_dict = row["entities"].get("entities", {})
        for ent_type, ent_list in entities_dict.items():
            for ent in ent_list:
                ent_text = ent['text']
                # Find all indices in English where this entity text appears
                ent_words = ent_text.split()
                en_indices = []
                # Search for consecutive token sequences matching the entity
                for i in range(len(en_tokens) - len(ent_words) + 1):
                    if en_tokens[i:i+len(ent_words)] == ent_words:
                        en_indices.extend(range(i, i + len(ent_words)))
                        break
                
                # Map those to Latin indices and then to Latin words
                la_indices = sorted(list(set(idx for en_i in en_indices for idx in align_map.get(en_i, []))))
                la_words = [la_tokens[i] for i in la_indices if i < len(la_tokens)]
                row_mappings.append({
                    "entity": ent_text,
                    "type": ent_type,
                    "en_indices": en_indices,
                    "la_indices": la_indices,
                    "la_text": " ".join(la_words)
                })
        
        results.append(row_mappings)
    
    df_results['mapped_entities'] = results
    
    # Step 3: Create BIO tags
    bio_tags = []
    for _, row in df_results.iterrows():
        la_tokens = row["sentences_la"].split()
        tags = ['O'] * len(la_tokens)
        
        for mapping in row['mapped_entities']:
            # Filter out entities with all lowercase tokens
            entity_tokens = [la_tokens[i] for i in mapping['la_indices'] if i < len(la_tokens)]
            if all(token.islower() for token in entity_tokens):
                continue
            
            # Apply BIO tags
            for i, la_idx in enumerate(mapping['la_indices']):
                if la_idx < len(tags):
                    prefix = 'B-' if i == 0 else 'I-'
                    tags[la_idx] = prefix + mapping['type']
        
        bio_tags.extend(tags)
    
    # Step 4: Add tags to tsv_df, skipping rows with tokens starting with # or empty tokens
    tag_idx = 0
    for idx, row in tsv_df.iterrows():
        token = row.get('TOKEN', '')
        # Skip rows where token starts with # or is empty
        if token.startswith('#') or token.strip() == '':
            tsv_df.at[idx, column_name] = ''
        else:
            if tag_idx < len(bio_tags):
                tsv_df.at[idx, column_name] = bio_tags[tag_idx]
                tag_idx += 1
            else:
                tsv_df.at[idx, column_name] = ''
    
    return tsv_df