file = open('neat.csv')

file.readline()

plids = set()
for line in file:
	record = line.split(',')
	plids.add(record[2])

plids = sorted(plids)

if __name__ == '__main__':
	print(plids)
