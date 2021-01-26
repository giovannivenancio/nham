import ctypes
import re, sys
import sys
from linux import *
from memutils import *

pid = int(sys.argv[1])
pid2 = int(sys.argv[2])

with Process.open_process(pid) as p:
    regions = p.list_mapped_regions(writeable_only=True)
    print(regions)

    chunks = []
    for region_start, region_stop in regions:
        region_buffer = (ctypes.c_byte * (region_stop - region_start))()
        chunk = p.read_memory(region_start, region_buffer)

        print("Region start   : ", region_start)
        print("Region stop    : ", region_stop)
        print("Region buffer  : ", region_buffer)
        print("Chunk          : ", chunk)
        print("--------------------------------------")
        chunks.append(chunk)

    #print(chunks)

    with Process.open_process(pid2) as p2:
        regions2 = p2.list_mapped_regions(writeable_only=True)

        print("src pid regions: ", len(regions))
        print("dst pid regions: ", len(regions2))

        i = 0

        for region_start2, region_stop2 in regions2:
            #base_addr = region_start2
            size = (region_stop2-region_start2)
            # print("\nRegion start   : ", region_start2)
            # print("Region stop    : ", region_stop2)
            # print("Total bytes: ", size)
            # print("type of size: ", type(size))
            # print("Writing %s to %s: " % (chunks[i], region_start2))
            # print("type of buffer: ", type(chunks[i]))
            #print("Base addr: ", base_addr)

            p2.write_process_memory(region_start2, size, chunks[i])

            # for b in chunks[i]:
            #     try:
            #         p2.pokedata(base_addr, b)
            #     except:
            #         pass
            # base_addr+=1
            #print("Final base addr: ", base_addr)
            #print("")
            i+=1
