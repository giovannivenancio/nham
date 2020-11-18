# METADATA
set encoding "utf8"
set terminal postscript eps enhanced color font 'verdana,24'
set output "../charts/throughput_failure_free.eps"

# COLORING
set style line 1 lt -1 lw 3 linecolor rgb "#CD5C5C" pi -1
set style line 2 lt -1 pt 7 lw 1 linecolor rgb "#696969" pi -30
set style line 3 lt -1 pt 5 lw 1 linecolor rgb "#CD5C5C" pi -30
set style line 4 lt -1 lw 3 linecolor rgb "#006400" pi -1
set style line 5 lt -1 lw 3 linecolor rgb "#D2691E" pi -1

# LABEL
set key right top
set key font "0.5"
set key spacing 1

# CHART CONFIGURATION
set style fill pattern 1 border -1
set boxwidth 0.9
set tic scale 0

set zeroaxis;
set grid ytics

# LABEL CONFIGURATION
set xlabel "Time (s)"
set ylabel "Throughput (Mbps)"
set yrange [0:1200]
set xrange [0:180]
set xtics 30

plot "data_throughput_baseline.dat" using 1:2 title 'Baseline' with linespoints ls 1, \
     "data_throughput_0r.dat"       using 1:2 title '0R'       with linespoints ls 2, \
     "data_throughput_1r-as.dat"    using 1:2 title '1R-AS'    with linespoints ls 3, \
     "data_throughput_1r-aa.dat"    using 1:2 title '1R-AA'    with linespoints ls 4, \
     "data_throughput_mr-aa.dat"    using 1:2 title 'MR-AA'    with linespoints ls 5
