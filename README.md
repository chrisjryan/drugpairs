# Drug pair finder
Christopher Ryan, July 2014.


`drugpairs.py` processes & analyzes comma-separated input files of the format requested ('patientID,date,drug' on each line). Command line options may be specified, and usage instructions can be seen via `python drugpairs.py -h`. In addition to input file name and output file name, the user can specify how many times each drug-pair should be co-administered in order to be listed in the output (via the `-Ncoadmin` option).

`random_dataset_maker.py` makes random input files the can be used by `drugpairs.py`. Usage instructions can again be read via `python random_dataset_maker.py -h`. The user may specify how many different drugs should be in the set, how many different patients, the minimum number of co-administration times for a subset of the drug-pairs (e.g., 25 in the `instructions.txt` given), and the number of drug-pairs that should reach this minimum (e.g., 7 pairs of drugs will show to be administered at least 25 times). In both files mentioned above, meaningful errors/warnings have been implemented to handle misformatted input and nonsensical user options. Drug lists are drawn as a random subset from the Top 300 prescriptions from 2005 as compiled by [RxList](http://www.rxlist.com/script/main/art.asp?articlekey=79509).



## Testing

A clean way to verify the correctness of these routines would be to run `dataset_maker.py` with the `-print_coad_counts` flag, then run `drugpairs.py` on its output file using once again the `-print_coad_counts` flag. In the first script, this flag outputs co-administration counts for each drug-pair gathered during random dataset generation. In the second script, this flag outputs co-administration counts as gathered during dataset processing. This will show both of these scripts output the same data, and that the output file of drugpairs.py contains each qualifying pair (with the minimal number of co-administration counts) as a comma-separated tuple, one per line, as requested by the instructions. For example, 

```
$ python random_dataset_maker.py -Ndrugs 5 -Npatients 5 -Ncoadmin 25 -Nmin_drugpairs_coadmin 3 -print_coad_counts   
drug1               drug2               co-administration count
Byetta              Flexeril            16
Byetta              Furosemide          21
Byetta              Prilosec            22
Byetta              Spiriva             26
Flexeril            Furosemide          14
Flexeril            Prilosec            22
Flexeril            Spiriva             19
Furosemide          Prilosec            19
Furosemide          Spiriva             25
Prilosec            Spiriva             25
$
$ python drugpairs.py -Ncoadmin 25 output_raw.csv -print_coad_counts
drug1               drug2               co-administration count
Byetta              Flexeril            16
Byetta              Furosemide          21
Byetta              Prilosec            22
Byetta              Spiriva             26
Flexeril            Furosemide          14
Flexeril            Prilosec            22
Flexeril            Spiriva             19
Furosemide          Prilosec            19
Furosemide          Spiriva             25
Prilosec            Spiriva             25
$
$ cat output_pairs.csv
Byetta,Spiriva
Furosemide,Spiriva
Prilosec,Spiriva
```

Units tests can be run via the doctest module:

```
$ python -m doctest -v drugpairs.py
...
5 passed and 0 failed.
Test passed.
```

```
$ python -m doctest -v random_dataset_maker.py
...
3 passed and 0 failed.
Test passed.
```


## Algorithmic complexity & scaling

Each line of the input file will be parsed and checked for formatting errors. For each line, which contains information about 1 drug that was given to 1 patient on 1 date, the subroutine checks to see if any other drug was given to this patient on this date. This list is contained in a 2-dimensional dict that may be accessed via `alldata[patient][date]`. Usage of a dict (i.e., hash table) here allows this search to be O(1) on average. However, the space complexity could be large -- O(N_patients x N_dates). The counts of co-administration dates are maintained in a similar 2-dimensional dict that is accessed as `coadmin_data[drug1][drug2]`. The space complexity here, O(N_drugs x N_drugs), should be much smaller. Similarly, though there are two one-time double loops over all drug-pairs in this 2d dict, this O(N_drugs^2) runtime will not likely bottleneck the program.

To increase efficiency with large datasets, the processing methods here could be run as batches in parallel on a cluster of compute nodes. Since the goal is to reduce all the raw data to a 'co-administration count', each node could run this count on a shard of the total data to achieve a local count. Each local count could be saved as a JSON file (or in a database), then re-loaded and combined upstream to get the total counts for the entire dataset. Note that, in addition to the 'coadmin_count' data, each of these preliminary JSON file should contain metadata to describe the parameters used to process the data set. 



## Extensions and further testing

- Additional checks might include making sure that the dates are valid beyond the YYYY-MM-DD format -- to check that they are not in the future, that month numbers are not greater than 12, and that dates are not impossible (e.g., 1990-02-30). Also, lowercase & uppercase drug names should be registered as the same.
- `drugpairs.check_line_format(l)` could also be a method to cleaning (rather than skipping) particular misformatted data. For example, it should be straightforward to read dates like '2012 - 01 - 14' and correct them to '2012-01-14'.