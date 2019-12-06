#set terminal pngcairo nocrop enhanced font "verdana,16" size 1920,1080
set terminal postscript eps enhanced color font 'verdana,24'
#set output "resiliency_performance.png"
set output "resiliency_performance.eps"

C = "#99ffff"; Cpp = "#4671d5"; Java = "#505050"; Python = "#f36e00"

#set key outside
set key right top
set key font "1"
set key spacing 1

set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
#set style fill pattern 1 border -1
set boxwidth 0.9
set tic scale 0

set xlabel "Number of VNFs"
set xtics nomirror

set ylabel "CPU Usage (%)"
set grid ytics lw 1 lc rgb "#505050"
set yrange [0:100]
set ytics 10


# 2, 3, 4, 5 are the indexes of the columns; 'fc' stands for 'fillcolor'
plot 'performance.data' using 2:xtic(1) fs pattern 1 ti col fc rgb C, '' u 3 fs pattern 2 ti col fc rgb Cpp, '' u 4 lt 2 ti col fc rgb "#406090", '' u 5 lc rgb Python fs pattern 4 ti col
