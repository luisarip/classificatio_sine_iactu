# classificatio_sine_iactu
Zero-Shot NERC in Latin with GLiNER2

The .py files are not called directly as scripts, so that users can import and extend individual functions — for example, adding new translation backends in `translator.py`.

- `from tsv_to_sentences import extract_sentences_from_tsv`: This function reads the .tsv file properly. Rows that start with "#" are skipped, and sentences are saved separately taking the "EndOfSentence" marker at "MISC" column as the delimiter between sentences. Joining sentences this way is necessary for the step of translation and input to the zero-shot model. Some checks are included to handle cases where the first row is not parsed as a header.

- `from translator import translate_latin_to_english`: Call to the [Google Translator API](https://pypi.org/project/deep-translator/), with some delay for the calls not to be blocked.

- `from gliner_latin import GLatiNER`: Loading zero-shot NERC model (default model is [fastino/gliner2-multi-v1](https://huggingface.co/fastino/gliner2-multi-v1), while passing the tagset saved in `taxonomies.json`. In that document, different label encodings are being saved as a dictionary. When running the model, the desired label set must be specified (in this case, "coarse_labels" or "fine_labels"). This function returns a dataframe with the original and translated sentences in parallel, with a column including entities extracted and confidence score.

- In `rule_based_processor.py` I included all the rule-based correctors I applied to post-process the results: in `filter_entities`, all entities below a confidence threshold are filtered out, and the function `enforce_label_consistency` ensures consistent label assignment across mentions of the same entity. 

- `from alignment import align_latin, align_english`: Two different functions perform the alignment, depending on whether the text has been translated. In case of working with translated English text, the alignment is performed using [simalign](https://github.com/cisnlp/simalign) with [UGARIT/grc-alignment](https://huggingface.co/UGARIT/grc-alignment) embeddings. Entities that are not uppercased are filtered out, and the results are converted to BIO format and projected back onto the original TSV.
