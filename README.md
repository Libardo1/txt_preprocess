txt_preprocess
==============

Tools for creating ngrams from text files with option to stem words and remove punctuation and stop words.

Usage:

```python
python ngrams_generate.py -s source_directory -t target_directory --min 1 --max 3 --nc 2 --clean --stem --stop
```


min - the smallest ngram to generate, default is 1 (i.e. unigram)
max - the largesest ngram to generate, default is 3 (i.e. trigram)
nc - number of cores to use, default is 1
clean - using this flag will lowercase text and remove punctuation and digits
stem - using this flag will stem words
stop - using this flag will remove common stop words

For each file in the source directory, the script will output a file in the target directory.

Here is an example output:

```
interest_income_2,1
telephone_1,1
revenue_subsidiary_level_3,1
subsidiary_1,2
processinc_supplies_2,1
```

The number after the comma represents the count for that ngram in the file.
The number directly before the comma is the length of the ngram.
