#set terminal pngcairo nocrop enhanced font "verdana,16" size 1920,1080
set terminal postscript eps enhanced color font 'verdana,24'
#set output "recovery.png"
set output "recovery.eps"

unset key

#set boxwidth 0.4

set style data histogram
set style histogram cluster gap 1 errorbars
set style fill solid border -1

set format xy "%g"
set tic scale 0

set xlabel "Resiliency Mechanism"
#set xtics nomirror

set ylabel "Average Recovery Time (s)"
set logscale y
set grid ytics lw 1 lc rgb "#505050"
set yrange [0.0001:10]
set xtics ("0R" 0, "1R-AS" 1, "1R-AA" 2, "NR-LB" 3)

plot "data.dat" using 2:3 lt rgb "#406090"
