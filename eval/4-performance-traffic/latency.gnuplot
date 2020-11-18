# METADATA
set encoding "utf8"
set terminal postscript eps enhanced color font 'verdana,24'
set output "../charts/latency.eps"

# COLORING
color_one = "#99ffff"; color_two = "#4671d5"; color_three = "#505050"; color_four = "#f36e00"; color_five = "#aadc32";

# LABEL
set key right top
set key font "1"
set key spacing 1

# CHART CONFIGURATION
set style data histogram
set style histogram cluster gap 1 errorbars
#set style fill solid border -1
set style fill pattern 1 border -1
set boxwidth 0.9
set tic scale 0

# LABEL CONFIGURATION
set xlabel "SFC Length"
set ylabel "Average Latency per Packet (ms)"

set xtics nomirror
set grid ytics lw 1 lc rgb "#505050"
set yrange [0:100]
set ytics 10
set xtics ("1" 0, "2" 1, "4" 2, "8" 3, "16" 4)

plot 'data_latency.dat' using 2:7  fs pattern 1 ti col, \
     'data_latency.dat' using 3:8  fs pattern 2 ti col, \
     'data_latency.dat' using 4:9  fs pattern 5 ti col, \
     'data_latency.dat' using 5:10 fs pattern 4 ti col, \
     'data_latency.dat' using 6:11 fs pattern 7 ti col
