# METADATA
set encoding "utf8"
set terminal postscript eps enhanced color font 'verdana,24'
set output "../charts/3-performance_cpu.eps"

color_one = "#99ffff"; color_two = "#4671d5"; color_three = "#505050"; color_four = "#f36e00"
darkcyan = "#008B8B"
darkmagenta = "#8B008B"

# LABEL
set key top right horizontal
set key maxcols 2
set key font "0.25"
set key spacing 1

# CHART CONFIGURATION
set style data histogram
set style histogram cluster gap 1 errorbars
set style fill solid border -1

set format xy "%g"
set boxwidth 0.9
set tic scale 0

# LABEL CONFIGURATION
set xlabel "SFC Length"
set ylabel "Average CPU Usage (%)"

set grid ytics lw 1 lc rgb "#505050"
set yrange [0:100]
set ytics 10
set xtics ("1" 0, "2" 1, "4" 2, "8" 3)

# PLOT DATA
plot 'data_cpu.dat' using 2:6 fs pattern 4 ti col lc rgb darkmagenta, \
     'data_cpu.dat' using 3:7 fs pattern 2 ti col, \
     'data_cpu.dat' using 4:8 fs pattern 1 ti col, \
     'data_cpu.dat' using 5:9 fs pattern 3 ti col lc rgb darkcyan
