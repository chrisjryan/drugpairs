




### strategy 1: since checking is done as the data structures are being built, 
# there won't be double loops to check for co-indidentally administatrered drugs. 
# This should accomplish the assigned task for files >>25 lines.

# dict {key->patientIDs: val->dict {key->drugs: val-> dates}

# as you build this dict, add to another dict:
#	{key->(drug1, drug2): val: (patient, date))}


from collections import defaultdict
import json
import argparse



# def load_JSON()


def save_JSON(data, filename = 'output.json'):
	with open(filename,'w') as outfile:
		json.dump(data, outfile, sort_keys=True, indent=4, separators=(',', ': '))



def read_analyze(filename, Ncoadmin):

	# might not need both of these. At least alldata would be good for outputting (easy to read back in.)
	alldata = defaultdict(lambda : defaultdict(list))
	coadmin_data = defaultdict(lambda : defaultdict(list))

	with open(filename) as f:
		for l in f:
			# check that only 3 fields were gotten, else exit.

			patient, date, drug1 = l.split(',')
			drug1 = drug1.rstrip('\n')

			# insert into the dict containing co-administration data:
			for drug2 in alldata[patient][date]:
				## check for redundant data
				coadmin_data[drug1][drug2].append((date, patient))
				coadmin_data[drug2][drug1].append((date, patient))

			alldata[patient][date].append(drug1)


	return coadmin_data

	# DEBUG: show full JSON data:
	# print json.dumps(alldata, sort_keys=True, indent=4, separators=(',', ': '))
	print json.dumps(drug_coadmin, sort_keys=True, indent=4, separators=(',', ': '))


if __name__ == "__main__":

	# parse the terminal input:
	Ncoadmin_default = 25
	desc = """This script will read in a CSV file containing drug administration 
	records (patientID, date of admin, drug name) and identify which pairs 
	of drugs were adminitered together N times (N=%i by default). Note that 
	the data are expected to be clean -- the date is consistently formatted 
	and there is only 1 valid name for each drug.""" % Ncoadmin_default
	parser = argparse.ArgumentParser(description=desc, formatter_class=argparse.ArgumentDefaultsHelpFormatter)
	parser.add_argument('filename', help='Raw CSV file containing comma separated 3-tuples (patient ID, date formated as YYYY-MM-DD, drug name)')
	parser.add_argument('-Ncoadmin', help="The minimum number of co-administered times for each drug in the output file.", type=int, default=Ncoadmin_default)
	args = parser.parse_args()

	# read the file & analyze for co-administration:
	coadmin_data = read_analyze(args.filename, args.Ncoadmin)

	# Build a list of drugs coadministered > N.coadmin times:
	l = [(drug1, drug2, len(coadmins)) \
	             for drug1, innerdict in coadmin_data.iteritems() \
	             for drug2, coadmins in innerdict.iteritems() \
	             if len(coadmins) >= args.Ncoadmin and drug1 < drug2]

	print l

	# save_JSON(alldata)
