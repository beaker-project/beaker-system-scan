#!/usr/bin/python
import unittest

try:
    import json
except ImportError:
    import simplejson as json

import sys
from systemscan import main
import os

class SystemScanTest(unittest.TestCase):

    def setUp(self):
        # Dumping 500 lines of xml directly into a unit test is not ok
        inputxml = open("./test_systemscan_xml").read()
        self.out = main.read_inventory(input_xml=inputxml, arch='x86_64',
                                       proc_cpuinfo=os.path.abspath('./test_proc_cpuinfo'))
        self.i686 = main.read_inventory(input_xml=inputxml, arch='i686',
                                       proc_cpuinfo=os.path.abspath('./test_proc_cpuinfo'))

    def test_read_inventory_devices(self):
        f = open('expected_devices.json')
        devicelist = json.loads(f.read())
        self.assertEquals(self.out['Devices'], devicelist)
        f.close()

    def test_read_inventory_cpu(self):
        self.assertEquals('x86_64', self.out['Arch'][0])
        self.assertEquals('GenuineIntel', self.out['Cpu']['vendor'])
        self.assertEquals('Xeon', self.out['Cpu']['modelName'])

        expected_flags = open('expected_cpu_flags').read().split()
        self.assertTrue(len(expected_flags), len(self.out['Cpu']['CpuFlags']))
        for flag in expected_flags:
            self.assertTrue(flag in self.out['Cpu']['CpuFlags'])

    # https://bugzilla.redhat.com/show_bug.cgi?id=1212307
    def test_read_inventory_ia64(self):
        inputxml = open("./test_lshw_ia64_xml").read()
        out = main.read_inventory(input_xml=inputxml, arch='ia64',
                                       proc_cpuinfo=os.path.abspath('./test_proc_cpuinfo_ia64'))
        self.assertEquals('ia64', out['Arch'][0])
        self.assertEquals('GenuineIntel', out['Cpu']['vendor'])
        self.assertEquals('Itanium 2', out['Cpu']['modelName'])
        self.assertEquals(1, out['Cpu']['family'])
        expected_flags = ['branchlong', '16-byte atomic ops']
        self.assertTrue(len(expected_flags), len(self.out['Cpu']['CpuFlags']))
        self.assertEquals(expected_flags, out['Cpu']['CpuFlags'])
        self.assertEquals(0, out['Cpu']['stepping'])

    # https://bugzilla.redhat.com/show_bug.cgi?id=1212310
    def test_read_inventory_s390x(self):
        inputxml = open("./test_lshw_s390x_xml").read()
        out = main.read_inventory(input_xml=inputxml, arch='s390x',
                                       proc_cpuinfo=os.path.abspath('./test_proc_cpuinfo_s390x'))
        self.assertEquals('s390x', out['Arch'][0])
        self.assertEquals('IBM/S390', out['Cpu']['vendor'])
        expected_flags = [u'esan3', u'highgprs', u'dfp', u'stfle', u'ldisp', u'eimm', u'zarch', u'etf3eh', u'msa']
        self.assertEquals(expected_flags, out['Cpu']['CpuFlags'])

    def test_map_32bit_archs(self):
        self.assertEquals('i386', self.i686['Arch'][0])

if __name__ == "__main__":
    unittest.main()
