import sys

dir = sys.argv[1]

type = 'cooldown'
#type = 'num_vnfs'

if type == 'cooldown':
    files = [
        'cooldown_1000_1r-aa.log',
        'cooldown_1000_nr-lb.log',
        'cooldown_500_1r-aa.log',
        'cooldown_500_nr-lb.log',
        'cooldown_250_1r-aa.log',
        'cooldown_250_nr-lb.log',
        'cooldown_100_1r-aa.log',
        'cooldown_100_nr-lb.log'
    ]
elif type == 'num_vnfs':
    files = [
        'vnf_1_1r-aa.log',
        'vnf_16_nr-lb.log',
        'vnf_2_1r-as.log',
        'vnf_4_1r-as.log',
        'vnf_8_1r-as.log',
        'vnf_1_1r-as.log',
        'vnf_1_nr-lb.log',
        'vnf_2_nr-lb.log',
        'vnf_4_nr-lb.log',
        'vnf_8_nr-lb.log',
        'vnf_16_1r-aa.log',
        'vnf_2_1r-aa.log',
        'vnf_4_1r-aa.log',
        'vnf_16_1r-as.log',
        'vnf_1_sr.log',
        'vnf_8_1r-aa.log'
]

for file in files:
    with open(dir + '/' + file, 'r') as open_file:
        print file
        for line in open_file.readlines()[5:]:
            print line.split(',')[0].replace('.', ',')
