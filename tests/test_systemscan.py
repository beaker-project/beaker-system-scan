#!/usr/bin/python
import unittest

try:
    import json
except ImportError:
    import simplejson as json

import lxml.etree
import sys
from systemscan import main
import os

class SystemScanTest(unittest.TestCase):

    def test_read_inventory_hp_z420(self):
        inputxml = lxml.etree.parse('hp-z420.xml')
        expected = json.load(open('hp-z420.expected.json'))
        out = main.read_inventory(inputxml, arch='x86_64',
                proc_cpuinfo=os.path.abspath('hp-z420.cpuinfo.txt'))
        self.assertEquals(expected, out)

    # https://bugzilla.redhat.com/show_bug.cgi?id=1212307
    def test_read_inventory_ia64(self):
        inputxml = lxml.etree.parse('./test_lshw_ia64_xml')
        out = main.read_inventory(inputxml, arch='ia64',
                                       proc_cpuinfo=os.path.abspath('./test_proc_cpuinfo_ia64'))
        self.assertEquals('ia64', out['Arch'][0])
        self.assertEquals('GenuineIntel', out['Cpu']['vendor'])
        self.assertEquals('Itanium 2', out['Cpu']['modelName'])
        self.assertEquals(1, out['Cpu']['family'])
        expected_flags = ['branchlong', '16-byte atomic ops']
        self.assertEquals(expected_flags, out['Cpu']['CpuFlags'])
        self.assertEquals(0, out['Cpu']['stepping'])

    # https://bugzilla.redhat.com/show_bug.cgi?id=1212310
    def test_read_inventory_s390x(self):
        inputxml = lxml.etree.parse('./test_lshw_s390x_xml')
        out = main.read_inventory(inputxml, arch='s390x',
                                       proc_cpuinfo=os.path.abspath('./test_proc_cpuinfo_s390x'))
        self.assertEquals('s390x', out['Arch'][0])
        self.assertEquals('IBM/S390', out['Cpu']['vendor'])
        expected_flags = [u'esan3', u'highgprs', u'dfp', u'stfle', u'ldisp', u'eimm', u'zarch', u'etf3eh', u'msa']
        self.assertEquals(expected_flags, out['Cpu']['CpuFlags'])

    def test_map_32bit_archs(self):
        inputxml = lxml.etree.parse('hp-z420.xml')
        i686 = main.read_inventory(inputxml, arch='i686',
                proc_cpuinfo=os.path.abspath('hp-z420.cpuinfo.txt'))
        self.assertEquals('i386', i686['Arch'][0])

    def test_read_inventory_aarch64(self):
        inputxml = lxml.etree.parse('apm-mustang.xml')
        expected = json.load(open('apm-mustang.expected.json'))
        out = main.read_inventory(inputxml, arch='aarch64')
        self.assertEquals(expected, out)

    def test_read_inventory_x86_kvm_guest(self):
        inputxml = lxml.etree.parse('x86-kvm-guest.xml')
        expected = json.load(open('x86-kvm-guest.expected.json'))
        out = main.read_inventory(inputxml, arch='x86_64',
                proc_cpuinfo=os.path.abspath('x86-kvm-guest.cpuinfo.txt'))
        self.assertEquals(expected, out)

if __name__ == "__main__":
    unittest.main()
