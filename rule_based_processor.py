"""
Module for rule-based post-processing of Named Entity Recognition (NER) outputs.
Provides filtering by confidence and global label consistency across a dataset.
"""

from collections import Counter

def filter_entities(row, threshold=0.65):
    """
    Filters entities inside:
    {"entities": {label: [entity_dict, ...]}}
    """

    if not isinstance(row, dict):
        return row

    entity_dict = row.get("entities", {})
    if not isinstance(entity_dict, dict):
        return row

    filtered = {
        label: [
            e for e in ents
            if isinstance(e, dict) and e.get("confidence", 0) >= threshold
        ]
        for label, ents in entity_dict.items()
    }

    return {"entities": filtered}

def enforce_label_consistency(series, min_occurrences=3):

    counts = {}

    # Pass 1 — collect counts
    for row in series:
        if not isinstance(row, dict):
            continue

        entity_dict = row.get("entities", {})
        for label, ents in entity_dict.items():
            for e in ents:
                key = e["text"].lower()
                counts.setdefault(key, Counter())[label] += 1

    majority = {
        text: cnt.most_common(1)[0][0]
        for text, cnt in counts.items()
        if sum(cnt.values()) >= min_occurrences
    }

    # Pass 2 — rebuild structure
    def relabel(row):
        if not isinstance(row, dict):
            return row

        entity_dict = row.get("entities", {})
        new_dict = {label: [] for label in entity_dict.keys()}

        for label, ents in entity_dict.items():
            for e in ents:
                new_label = majority.get(e["text"].lower(), label)
                new_dict.setdefault(new_label, []).append(e)

        return {"entities": new_dict}

    return series.apply(relabel)

if __name__ == "__main__":
    # Example usage / smoke test
    print("Post-processing module loaded successfully.")