#!/usr/bin/python
import unittest

try:
    import json
except ImportError:
    import simplejson as json

import sys
sys.path.append('../')
import main
import os

class SystemScanTest(unittest.TestCase):

    def setUp(self):
        # Dumping 500 lines of xml directly into a unit test is not ok
        inputxml = open("./test_systemscan_xml").read()
        self.out = main.read_inventory(input_xml=inputxml, arch='x86_64',
                                       proc_cpuinfo=os.path.abspath('./test_proc_cpuinfo'))

    def test_read_inventory_devices(self):
        f = open('expected_devices.json')
        devicelist = json.loads(f.read())
        for device in devicelist:
            self.assertTrue(device in self.out['Devices'], "Device missing, "
                            "or incorrectly reported: %s" % device['description'])
        f.close()

    def test_read_inventory_cpu(self):
        # Most cpu details are taken straight from proc, not the lshw xml
        # and so are not covered by this test

        self.assertEquals('x86_64', self.out['Arch'][0])
        self.assertEquals('Intel Corp.', self.out['Cpu']['vendor'])
        self.assertEquals('Xeon', self.out['Cpu']['modelName'])

        expected_flags = open('expected_cpu_flags').read().split()
        for flag in self.out['Cpu']['CpuFlags']:
            self.assertTrue(flag in expected_flags, flag)

    def test_read_inventory_ia64(self):
        inputxml = open("./test_lshw_ia64_xml").read()
        out = main.read_inventory(input_xml=inputxml, arch='ia64',
                                       proc_cpuinfo=os.path.abspath('./test_proc_cpuinfo_ia64'))
        self.assertEquals('ia64', out['Arch'][0])
        self.assertEquals('Intel Corp.', out['Cpu']['vendor'])
        self.assertEquals('Itanium 2', out['Cpu']['modelName'])
        self.assertEquals(2, out['Cpu']['family'])
        # This is a bug that needs to be fixed, the test just
        # tests the current state.
        self.assertFalse(out['Cpu']['CpuFlags'])

if __name__ == "__main__":
    unittest.main()
