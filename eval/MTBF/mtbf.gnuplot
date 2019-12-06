set terminal pngcairo nocrop enhanced font "verdana,16" size 1920,1080
set output "availability.png"

C = "#99ffff"; Cpp = "#4671d5"; Java = "#ff0000"; Python = "#f36e00"

set key outside
set key right center
set key font "2"
set key spacing 2


set style data histogram
set style histogram cluster gap 1
set style fill solid border -1
set boxwidth 0.9
set tic scale 0

set xlabel "Resiliency Mechanism"
set xtics nomirror

set ylabel "Time (s)"
set grid ytics lw 1 lc rgb "#505050"
set yrange [90:100]
set ytics 1


# 2, 3, 4, 5 are the indexes of the columns; 'fc' stands for 'fillcolor'
plot 'recovery.data' using 2:xtic(1) ti col fc rgb C, '' u 3 ti col fc rgb Cpp, '' u 4 ti col fc rgb Java, '' u 5 ti col fc rgb Python
