# classificatio_sine_iactu
Zero-Shot NERC in Latin with GLiNER2

I didn't call the .py files as the functions, so people can reuse the .py files adding as new functions modifications to this basis. For example, in `translator.py`, different functions can be created with different names calling to different APIs. 

- `from tsv_to_sentences import extract_sentences_from_tsv`: This function reads the .tsv file properly. Rows that start with "#" are skipped, and sentences are saved separately taking the "EndOfSentence" marker at "MISC" column as the delimiter between sentences. Joining sentences this way is necessary for the step of translation and input to the zero-shot model. Some lines are robust in case the first row has not been read as a header.

- `from translator import translate_latin_to_english`: Call to the Google Translator API, with some delay for the calls not to be blocked.

- ``
