import sys
import random

data = sys.argv[1]
threshold_min = int(sys.argv[2])
threshold_max = int(sys.argv[3])

new_data = []
with open(data, 'r') as f:
    lines = f.readlines()
    for line in lines:
        if ' ' in line:
            th = float(line.split(' ')[1].strip('\n'))
        elif '\t' in line:
            th = float(line.split('\t')[1].strip('\n'))
        new_value = th
        if th > threshold_max:
            new_value = ((threshold_max + threshold_min)/2) - random.randint(1, 3)
            #print "valor maior: %f virou %f" % (th, new_value)
        elif th < threshold_min:
            new_value = ((threshold_max + threshold_min)/2) + random.randint(1, 3)
            #print "valor menor"
        new_data.append(new_value)

for i in range(len(new_data)):
    print i+1, new_data[i]
