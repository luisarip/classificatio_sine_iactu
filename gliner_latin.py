from gliner2 import GLiNER2
import pandas as pd
import json

class GLatiNER:
    def __init__(self, model_name="fastino/gliner2-multi-v1", taxonomy_file="taxonomies.json"):
        self.extractor = GLiNER2.from_pretrained(model_name)

        # Load all taxonomies from the JSON file
        with open(taxonomy_file, 'r', encoding='utf-8') as f:
            self.all_taxonomies = json.load(f)

    def process(self, original_sentences, taxonomy_name, target_sentences=None):
        """
        Runs NER on target_sentences and maps results back to original_sentences.
        taxonomy_name: the key in JSON file ('coarse_labels', 'fine_labels')
        """
        selected_labels = self.all_taxonomies.get(taxonomy_name, {})
        rows = []
        eval_sentences = []

        # If no target provided, treat original as the text to extract from
        if target_sentences is None:
            eval_sentences = original_sentences
        else:
            eval_sentences = target_sentences


        for orig, target in zip(original_sentences, eval_sentences):
            entities = self.extractor.extract_entities(target, selected_labels, include_confidence=True)
            data = {"sentences_la": orig}
            if target_sentences is not None:
                data["sentences_en"] = target
            data["entities"] = entities
            rows.append(data)
        return pd.DataFrame(rows)