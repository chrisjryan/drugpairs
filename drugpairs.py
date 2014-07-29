#!/usr/bin/env python

from collections import defaultdict
import json
import argparse
import sys
import re
import os



def save_JSON(data, filename = 'output.json'):
	"""
	Simple implementation of JSON file saving with some default parameters.
	"""
	with open(filename,'w') as outfile:
		json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))


def check_line_format(l):
	"""
	Checks to make sure that line l in the input file is formatted such that it 
	can be processed further in this script. This function could be extended to 
	automatically clean data that are dirty in a specific way.
	Notes: (i) precompiled regex patterns would speed up this routine, (ii) date 
	are verified to me YYYY-MM-DD format, where Y/M/D are [0-9], but not checked 
	beyond that, and (iii) no format restrictions are currently places on drug 
	name. All this, and other checks, could be implemented straightforwardly.
	>>> check_line_format('I861,2013-02-20,Azithromycin')
	['I861', '2013-02-20', 'Azithromycin']
	>>> check_line_format('I861,2013-02-20,Azithr,omycin')
	Warning: skipping line containing comma-separated fields !=3: 
	I861,2013-02-20,Azithr,omycin
	>>> check_line_format('I861,20013-0200-2,Azithromycin')
	Warning: skipping line containing an improperly formatted date field: 
	20013-0200-2
	>>> check_line_format('IZ50861,2013-02-20,Azithromycin')
	Warning: skipping line containing an improperly formatted patientID field: 
	IZ50861
	>>> check_line_format('I861,2013-02-20,Azithrom234^&*^*&@^#072934ycin')
	['I861', '2013-02-20', 'Azithrom234^&*^*&@^#072934ycin']
	"""

	splitline = l.split(',')
	if len(splitline) != 3:
		print 'Warning: skipping line containing comma-separated fields !=3: \n%s' % l
		return 
	elif re.match('[A-Z][0-9]{3}$',splitline[0]) is None:
		print 'Warning: skipping line containing an improperly formatted patientID field: \n%s' % splitline[0]
		return 
	elif re.match('[0-9]{4}-[0-9]{2}-[0-9]{2}$',splitline[1]) is None:
		print 'Warning: skipping line containing an improperly formatted date field: \n%s' % splitline[1]
		return 
	else:
		return splitline


def read_analyze(filename, Ncoadmin):
	"""
	Read data from a file & count when pairs of drugs are co-administered. Each
	line of the file is checked to contain 3 fields. 'coadmin_data' is saved as 
	a dict whose values are nested dicts, whose values are lists of 2-tuples: 
	{'drug1': {'drug2': [(date1,patient1), (date2,patient2), ...]}}.
	Note that coadmin_data stores redundantly at this point -- a given 
	(administration date, patient) tuple will be added to both 
	coadmin_data[drug1][drug2] and coadmin_data[drug2][drug1].
	Lines containing redundant data will be skipped.
	"""

	# might not need both of these. At least alldata would be good for outputting (easy to read back in.)
	alldata = defaultdict(lambda : defaultdict(list))
	coadmin_data = defaultdict(lambda : defaultdict(list))

	with open(filename) as f:
		for l in f:

			splitline = check_line_format(l)
			if splitline:
				# parse the new line's data:
				patient, date, drug1 = splitline
				drug1 = drug1.rstrip('\n')

				# If another drug has been given on this date to this patient,
				# save this co-administration data:
				for drug2 in alldata[patient][date]:
					if (date, patient) not in coadmin_data[drug1][drug2] and\
					   (date, patient) not in coadmin_data[drug2][drug1]:
						coadmin_data[drug1][drug2].append((date, patient))
						coadmin_data[drug2][drug1].append((date, patient))
					else:
						print 'Warning: skipping line containing redundant (already-processed) co-administration data: \n%s,%s' % (drug1, drug2)

				alldata[patient][date].append(drug1)

	return coadmin_data, alldata


def print_coad_data(coadmin_data):
	# reconstruct the coad_counts dict:
	coad_counter = defaultdict(lambda : defaultdict(list))
	for d1, innerdict in coadmin_data.iteritems():
	    for d2, coadmins in innerdict.iteritems():
	    	if d1 < d2:
		    	coad_counter[d1][d2] = len(coadmins)

	# print a co-administration table to the screen:
	print '%-20s%-20s%-s' % ('drug1','drug2','co-administration count')
	for d1, innerdict in sorted(coad_counter.iteritems()):
	    for d2, coadmins in sorted(innerdict.iteritems()):
	    	print '%-20s%-20s%-i' % (d1, d2, coadmins)


if __name__ == "__main__":

	# parse the terminal input:
	Ncoadmin_default = 25
	desc = """This script will read in a CSV file containing drug administration 
	records (patientID, date of admin, drug name) and identify which pairs 
	of drugs were administered together N times (N=%i by default). Note that 
	the data are expected to be clean -- the date is consistently formatted 
	and there is only 1 valid name for each drug.""" % Ncoadmin_default
	parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('infilename', help='Raw CSV file containing comma separated 3-tuples (patient ID, date formated as YYYY-MM-DD, drug name)')
	parser.add_argument('-outfilename', help='The name of the output file.', type=str, default = 'output_pairs.csv')
	parser.add_argument('-Ncoadmin', help="The minimum number of co-administered times for each drug in the output file.", type=int, default=Ncoadmin_default)
	parser.add_argument('-print_coad_counts', help='Whether to print the total counts of all co-administered drugs to the terminal.', action='store_true')
	args = parser.parse_args()

	# check that the file exists:
	if not os.path.isfile(args.infilename):
		sys.exit("Error: file '%s' not found." % args.infilename)

	# read the file & analyze for co-administration:
	coadmin_data, alldata = read_analyze(args.infilename, args.Ncoadmin)

	# Build a list of drugs co-administered > N.coadmin times:
	drugpairs = [(drug1, drug2) \
	             for drug1, innerdict in coadmin_data.iteritems() \
	             for drug2, coadmins in innerdict.iteritems() \
	             if len(coadmins) >= args.Ncoadmin and drug1 < drug2]

	# write data about co-administered drugs to the output file:
	with open(args.outfilename,'w') as f:
		for pair in sorted(drugpairs):
			f.write(','.join(pair)+'\n')
			# if args.print_coad_counts:
			# 	print ','.join(pair)#+'\n'

	# if requested, print some info about data processing to the terminal:
	if args.print_coad_counts:
		print_coad_data(coadmin_data)