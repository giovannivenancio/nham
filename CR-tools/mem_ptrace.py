#!/usr/bin/env python
import ctypes, re, sys

## Partial interface to ptrace(2), only for PTRACE_ATTACH and PTRACE_DETACH.
c_ptrace = ctypes.CDLL("libc.so.6").ptrace
c_pid_t = ctypes.c_int32 # This assumes pid_t is int32_t
c_ptrace.argtypes = [ctypes.c_int, c_pid_t, ctypes.c_void_p, ctypes.c_void_p]

def ptrace(attach, pid):
    """ATTACH or DETACH a process.
    Used to stop/resume execution when a checkpoint is being performed.
    """

    #PTRACE_ATTACH or PTRACE_DETACH
    op = ctypes.c_int(16 if attach else 17)
    c_pid = c_pid_t(pid)
    null = ctypes.c_void_p()

    err = c_ptrace(op, c_pid, null, null)

    if err != 0:
        print err

def ptrace_write(pid, addr, data):
    "op 5 is POKEDATA"

    print "writing"
    op = ctypes.c_int(5)
    c_pid = c_pid_t(pid)
    err = c_ptrace(op, c_pid, addr, data)

    if err != 0:
        print err
    else:
        print "ok?"

def dump(pid, dump_mem):
    """Dump the contents of memory to DB or another VNF."""

    memory_permissions = 'rw'
    memory_dump = open(dump_mem, 'wb')

    # sequentially read memory map
    with open('/proc/%d/maps' % pid, 'r') as maps_file:
        with open('/proc/%d/mem' % pid, 'rb+', 0) as mem_file:
            # for each mapped region
            for line in maps_file.readlines():
                m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r][-w])', line)

                memory_region = line.split(' ')[-1].strip('\n')

                #if memory_region in ['[stack]', '[heap]', '[vvar]', '[vdso]', '[vsyscall]']:

                if m.group(3) == memory_permissions:
                    start = int(m.group(1), 16)

                    if start > 0xFFFFFFFFFFFF:
                        continue

                    end = int(m.group(2), 16)

                    # seek to region start
                    mem_file.seek(start)

                    # read region contents
                    chunk = mem_file.read(end - start)
                    memory_dump.write(chunk)

    memory_dump.close()

def replace_dump(pid, dump_mem, only_writable=True):
    memory_permissions = 'rw' if only_writable else 'r-'
    memory_dump = ''

    dump_mem_fd = open(dump_mem, 'rb')

    # sequentially read memory map
    with open('/proc/%d/maps' % pid, 'r') as maps_file:
        with open('/proc/%d/mem' % pid, 'rb+', 0) as mem_file:
            # for each mapped region
            for line in maps_file.readlines():
                m = re.match(r'([0-9A-Fa-f]+)-([0-9A-Fa-f]+) ([-r][-w])', line)

                if m.group(3) == memory_permissions:
                    start = int(m.group(1), 16)

                    if start > 0xFFFFFFFFFFFF:
                        continue

                    end = int(m.group(2), 16)

                    # seek to region start
                    mem_file.seek(start)

                    # read region contents
                    chunk = dump_mem_fd.read(end - start)
                    #print chunk

                    # print "====================="
                    # print "start:"
                    # print start
                    # print m.group(1)
                    # print ""
                    # print "====================="
                    # print "end:"
                    # print end
                    # print m.group(2)
                    # print ""
                    # print "====================="

                    mem_file.write(chunk)
                    #memory_dump += chunk

    dump_mem_fd.close()

## Dump the readable chunks of memory mapped by a process
def cat_proc_mem(pid, dump_mem):
    ptrace(True, int(pid))
    memory_dump = dump(int(pid), dump_mem)
    ptrace(False, int(pid))

def restore(pid, dump_mem):
    ptrace(True, int(pid))
    replace_dump(int(pid), dump_mem)
    ptrace(False, int(pid))

if __name__ == "__main__":
    pid = sys.argv[2]
    dump_mem = sys.argv[3]

    if sys.argv[1] == 'checkpoint':
        cat_proc_mem(pid, dump_mem)

    elif sys.argv[1] == 'restore':
        restore(pid, dump_mem)
