#!/usr/bin/python
import unittest
import json

import sys
sys.path.append('../')
import main

class SystemScanTest(unittest.TestCase):

    def setUp(self):
        # Dumping 500 lines of xml directly into a unit test is not ok
        inputxml = open("./test_systemscan_xml").read()
        self.out = main.read_inventory(inputxml, 
                                       proc_cpuinfo='test_proc_cpuinfo')

    def test_read_inventory_devices(self):
        with open('expected_devices.json') as f:
           devicelist = json.loads(f.read())
        for device in devicelist:
            self.assertTrue(device in self.out['Devices'], "Device missing, "
                            "or incorrectly reported: %s" % device['description'])

    def test_read_inventory_cpu(self):
        # Most cpu details are taken straight from proc, not the lshw xml
        # and so are not covered by this test

        self.assertEquals('x86-64', self.out['Arch'][0])
        self.assertEquals('Intel Corp.', self.out['Cpu']['vendor'])
        self.assertEquals('Xeon', self.out['Cpu']['modelName'])

        expected_flags = open('expected_cpu_flags').read().split()
        for flag in self.out['Cpu']['CpuFlags']:
            self.assertTrue(flag in expected_flags, flag)

if __name__ == "__main__":
    unittest.main()
