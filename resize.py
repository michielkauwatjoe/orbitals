#!/usr/bin/env python3
from PIL import Image
import os

if not os.path.exists('output_s'):
    os.mkdir('output_s')

l = os.listdir('output')
base = 'res_c_num400_fs6_near0.0100_far0.1500_pa0.1000_pb0.0300_itt'

for fileName in sorted(l):
    if fileName.startswith(base):
        newName = fileName.replace(base, '')
        if len(newName) == 9:
            newName = '0' + newName
        im = Image.open('%s/%s' % ('output', fileName))
        w = h = 1000
        im = im.resize((w, h), Image.ANTIALIAS)
        im.save('%s/%s' % ('output_s', newName))
