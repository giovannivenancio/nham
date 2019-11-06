#!/usr/bin/env python

from nfvo import *
from vnfm import *
from vim import *
from nham import *

vim = VirtualizedInfrastructureManager()

type = 'container'
image = 'ubuntu'
cpu_count = int('2')
mem_limit = '512MB'

#c_id = vim.create_virtual_device(type, image, cpu_count, mem_limit)
vim.list_virtual_devices()
#vim.delete_virtual_device(c_id)
#vim.list_virtual_devices()
vim.purge_devices()
