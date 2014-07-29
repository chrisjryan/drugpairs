#!/usr/bin/env python

import argparse
from random import randint, sample
import string
import sys
from collections import defaultdict
import itertools
import json


def not_enough_coads(coad_counter, Ncoadmin, Nmin_drugpairs_coadmin):
	"""
	Return True if you need to generate more drug administration records to meet 
	the minimum number of drugs pairs that have the minimum number of times 
	co-administered. (Else, if you're done, return False.)
	>>> testdict = test = {'drug1':{'drug2':4, 'drug3':6}, 'drug2':{'drug3':2}, 'drug3':{}}
	>>> not_enough_coads(test, 4, 2)
	False
	>>> not_enough_coads(test, 4, 3)
	True
	"""
	count = 0 # number of drug pairs that have been administered >= Ncoadmin times.
	for d1, innerdict in coad_counter.iteritems():
	    for d2, coadmins in innerdict.iteritems():
	        if coad_counter[d1][d2] >= Ncoadmin:
	        	count += 1
			if count >= Nmin_drugpairs_coadmin:
				return False

	return True		


def initialize():
	"""
	Initialize several objects to generate a random dataset.
	"""
	# get a random list of Ndrugs drugs from a list of 300 drug names:
	with open('top300drugs.dat') as f:
		drugs_total = f.read().split('\n')
	drugs = sample(drugs_total, args.Ndrugs)

	# of that new list, choose a subset that will be co-administered Ncoadmin times:
	drugs_coad = sample(drugs, args.Nmin_drugpairs_coadmin)

	# get a list of random patientIDs:
	patients = ['%s%03d' % (string.ascii_uppercase[randint(0,25)], randint(0,999)) \
				for _ in range(args.Npatients)]

	return drugs, drugs_coad, patients


def parse_user_args(parser):
	"""
	A straightforward implementation of the argparse module.
	"""
	Ncoadmin_default = 25
	parser.add_argument('-Ndrugs', help='Number of different drugs in the random data set.', type=int, default = 3)
	parser.add_argument('-Npatients', help='Number of different patients in the random data set.', type=int, default = 4)
	parser.add_argument('-Nmin_drugpairs_coadmin', help="The number of drug that will be co-administered Ncoadmin times.", type=int, default=3)
	parser.add_argument('-Ncoadmin', help="The minimum number of co-administrations each drug-pair in the output file.", type=int, default=10)
	parser.add_argument('-outfilename', help='The name of the output file.', type=str, default = 'output_raw.csv')
	parser.add_argument('-print_coad_counts', help='Whether to print the total counts of all coadministered drugs to the terminal.', action='store_true')
	return parser.parse_args()


if __name__ == "__main__":

	# parse the terminal input:	
	desc = "Make a dataset for analysis by drugpairs.py. "
	parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	args = parse_user_args(parser)
	if args.Nmin_drugpairs_coadmin > args.Ndrugs:
		sys.exit("""The number of drugs that will be co-administered Ncoadmin times 
	should be less than or equal to the total number of drugs in the data set.""")

	# initialize objects:
	drugs, drugs_coad, patients = initialize()

	with open(args.outfilename,'w') as out:

		# zero-out a defaultdict that will count number of co-administered drugs:
		coad_counter = defaultdict(lambda : defaultdict(int))
		for d1,d2 in itertools.combinations(sorted(drugs_coad), 2):
			coad_counter[d1][d2] = 0

		# make drug administration data until you have enough:
		while not_enough_coads(coad_counter, args.Ncoadmin, args.Nmin_drugpairs_coadmin):

			# generate a random "doctor visit" (date, patient, [drugs administered]):
			date = '%04d-%02d-%02d' % (randint(1990,2013), randint(1,12), randint(1,28))
			patient = sample(patients,1)[0]
			drugs_visit = sample(drugs, randint(1,args.Ndrugs))

			# add to the output file:
			for d in drugs_visit:
				out.write('%s,%s,%s\n' % (patient, date, d))

			# add to the number of co-administered drugs:
			for d1,d2 in itertools.combinations(sorted(drugs_visit),2):
				# print d1,d2
				coad_counter[d1][d2] += 1

	if args.print_coad_counts:
		print '%-20s%-20s%-s' % ('drug1','drug2','co-administration count')
		for d1, innerdict in sorted(coad_counter.iteritems()):
		    for d2, coadmins in sorted(innerdict.iteritems()):
		    	print '%-20s%-20s%-i' % (d1, d2, coadmins)
		# print json.dumps(coad_counter, sort_keys=True, indent=4, separators=(',', ': '))


