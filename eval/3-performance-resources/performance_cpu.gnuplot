# METADATA
set encoding "utf8"
set terminal postscript eps enhanced color font 'verdana,24'
set output "../charts/performance_cpu.eps"

color_one = "#99ffff"; color_two = "#4671d5"; color_three = "#505050"; color_four = "#f36e00"

# LABEL
set key right top
set key font "1"
set key spacing 1

# CHART CONFIGURATION
set style data histogram
set style histogram cluster gap 1 errorbars
set style fill solid border -1
#set style fill pattern 1 border -1
set boxwidth 0.9
set tic scale 0

# LABEL CONFIGURATION
set xlabel "SFC Length"
set ylabel "Average CPU Usage (%)"

set xtics nomirror
set grid ytics lw 1 lc rgb "#505050"
set yrange [0:100]
set ytics 10
set xtics ("1" 0, "2" 1, "4" 2, "8" 3, "16" 4)

# PLOT DATA
plot 'data_cpu.dat' using 2:6 fs pattern 1 ti col fc rgb color_one,   \
     'data_cpu.dat' using 3:7 fs pattern 2 ti col fc rgb color_two,   \
     'data_cpu.dat' using 4:8 fs pattern 5 ti col fc rgb color_three, \
     'data_cpu.dat' using 5:9 fs pattern 4 ti col fc rgb color_four
