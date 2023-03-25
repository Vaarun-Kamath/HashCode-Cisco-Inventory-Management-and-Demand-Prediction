file = open('neat.csv')

file.readline()

plids = set()
quarters = set()
months = set()
for line in file:
	record = line.split(',')
	plids.add(record[2])
	# quarters.add(record[3])
	# months.add(record[4])

plids = sorted(plids)
quarters = sorted(quarters)
months = sorted(months)

if __name__ == '__main__':
	print(plids)
