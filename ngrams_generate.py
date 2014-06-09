# this program takes as input a directory with text files and converts each file into associated n-grams, from 1 to n
# python ngram_generate src_dir dst_dir smallest_ngram larget_ngram num_cores clean

import argparse
import re
import os
import pp
import csv
import string

parser = argparse.ArgumentParser()
parser.add_argument("-s","--src", help="Source directory")
parser.add_argument("-d","--dst", help="Destination directory")
parser.add_argument("--min", help="Min ngram length, default 1", default=1, type=int)
parser.add_argument("--max", help="Max ngram length, default 3", default=3, type=int)
parser.add_argument("--nc", help="Number of cores to use, default 1", default=1, type=int)
parser.add_argument("--clean", help="Flag for removing numbers and punctuation", action="store_true")
parser.add_argument("--stem", help="Flat for stemming", action="store_true")
parser.add_argument("--stop", help="Flat for removing stopwords", action="store_true")

args = parser.parse_args()

if not os.path.isdir(args.src):
    exit("ERROR: Source directory not found")

if not os.path.isdir(args.dst):
    exit("ERROR: Destination directory not found")

if args.stop:
    with open('stopwords.txt', 'rb') as f:
        stopwords = f.replace('\r', '').split('\n')
else:
    stopwords = []

file_list = os.listdir(args.src)[:41]
job_server = pp.Server(args.nc)

def create_ngram(file_list, source_directory, target_directory, stopwords, min_n, max_n, clean, stem):
    from collections import defaultdict
    from stemming.porter2 import stem as stemmer
    from nltk import ngrams
    punct = string.punctuation + string.digits
    os.chdir(source_directory)
    for file_name in file_list:
        long_gram= defaultdict(int)
        try:
            with open(file_name, 'rb') as f_in:
                text = f_in.read()
            if clean:
                text = ''.join(s for s in text if s not in punct).lower()
            text_list = re.split(r'[ \t\n\r]+', text)
            text_list = [word for word in text_list if word not in stopwords]
            if stem:
                text_list = [stemmer(word) for word in text_list]
            grams = [ngrams(text_list, gram_len) for gram_len in range(min_n, max_n + 1)]
            for gram in grams:
                for item in gram:
                    key = list(item)
                    key.extend(str(len(key)))
                    long_gram['_'.join(key)] += 1
            with open(target_directory + '/' + file_name.split('.')[0] + '_grams.csv','wb') as f_out:
                csvw = csv.writer(f_out)
                for k,v in long_gram.iteritems():
                    csvw.writerow([k, v])
        except Exception:
            #do error handling here
            return Exception
            pass
    return True



# how many files to send to each core
factor = int(round(len(file_list) / args.nc))

module_list = tuple(["stemming", "os", "re", "collections", "nltk", "csv", "string"])

src_dir = args.src
dst_dir = args.dst


min_n = args.min
max_n = args.max
clean = args.clean
stem = args.stem

print "sending jobs"
if args.nc > 1:
    processes = [job_server.submit(create_ngram, 
                               args=(file_list[(factor*i):(factor*(i+1))],
                                               src_dir, dst_dir, stopwords,
                                               min_n, max_n, clean, stem), 
                                               modules=module_list, 
                                               group='default') for i in xrange(args.nc - 1)]

processes.append(job_server.submit(create_ngram, 
                                   args=(file_list[(factor * (args.nc - 1)) : ], 
                                                   src_dir, dst_dir, stopwords,
                                                   min_n, max_n, clean, stem), 
                                                   modules=module_list, group='default'))

# TODO add check progress functionality and error checking
job_server.wait('default')

print 'done'