#set terminal pngcairo nocrop enhanced font "verdana,16" size 1920,1080
set terminal postscript eps enhanced color font 'verdana,24'
#set output "recovery.png"
set output "recovery.eps"

unset key

set boxwidth 0.4
set style fill solid 1.00
set format xy "%g"
set tic scale 0

set xlabel "Resiliency Mechanism"
set xtics nomirror

set ylabel "Time (s)"
set logscale y
set grid ytics lw 1 lc rgb "#505050"
set yrange [0.0001:10]

plot "data.dat" using 2:xticlabels(1) with boxes lt rgb "#406090"
