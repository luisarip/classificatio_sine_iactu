# Classificatio Sine Iactu — That Is, Zero-Shot NERC in Latin with GLiNER2
Developed by Luisa Ripoll-Alberola<sup>1,3</sup>, Fernando Nicolás-Flores<sup>2</sup> and Francisco Javier Muñoz Acebes<sup>3</sup> 

<sup>1</sup>Computational Humanities, Leipzig University

<sup>2</sup>Departamento de Prehistoria, Arqueología, Historia Antigua, Filología Griega y Filología Latina, Universidad de Alicante 

<sup>3</sup>Filología Digital, Universidad de Valladolid

Each .py file is a module containing one or more functions, intended to be imported rather than run directly as a script — for example, `translator.py` contains `translate_latin_to_english` but can be extended with additional translation backends.

- `from tsv_to_sentences import extract_sentences_from_tsv`: This function reads the .tsv file properly. Rows that start with "#" are skipped, and sentences are saved separately taking the "EndOfSentence" marker at "MISC" column as the delimiter between sentences. Joining sentences this way is necessary for the step of translation and input to the zero-shot model. Some checks are included to handle cases where the first row is not parsed as a header.

- `from translator import translate_latin_to_english`: Call to the [Google Translator API](https://pypi.org/project/deep-translator/), with some delay for the calls not to be blocked.

- `from gliner_latin import GLatiNER`: Loading zero-shot NERC model (default model is [fastino/gliner2-multi-v1](https://huggingface.co/fastino/gliner2-multi-v1), while passing the tagset saved in `taxonomies.json`. In that document, different label encodings are being saved as a dictionary. When running the model, the desired label set must be specified (in this case, "coarse_labels" or "fine_labels"). This function returns a dataframe with the original and translated sentences in parallel, with a column including entities extracted and confidence score.

- In `rule_based_processor.py` one can find all rule-based correctors applied to post-process the results: in `filter_entities`, all entities below a confidence threshold are filtered out, and the function `enforce_label_consistency` ensures consistent label assignment across mentions of the same entity. 

- `from alignment import align_latin, align_english`: Two different functions perform the alignment, depending on whether the text has been translated. In case of working with translated English text, the alignment is performed using [simalign](https://github.com/cisnlp/simalign) with [UGARIT/grc-alignment](https://huggingface.co/UGARIT/grc-alignment) embeddings. Entities that are not uppercased are filtered out, and the results are converted to BIO format and projected back onto the original TSV.

There is a Jupyter Notebook containing examples of usage in the "example" folder. 

### Declaration on AI

During the preparation of this repository, the authors used the models ChatGPT 5, Claude Sonnet 4.5 and 4.6, Gemini 3.1 Pro, and Copilot 4, in order to draft code, debug errors, and improve code efficiency. The authors reviewed and edited the content as needed and take full responsibility for the publication’s content.
