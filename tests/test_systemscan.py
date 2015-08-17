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

    def test_read_inventory_ia64(self):
        inputxml = lxml.etree.parse('hp-rx1620.xml')
        expected = json.load(open('hp-rx1620.expected.json'))
        out = main.read_inventory(inputxml, arch='ia64',
                proc_cpuinfo=os.path.abspath('hp-rx1620.cpuinfo.txt'))
        self.assertEquals(expected, out)

    def test_read_inventory_s390x(self):
        inputxml = lxml.etree.parse('s390-guest.xml')
        expected = json.load(open('s390-guest.expected.json'))
        out = main.read_inventory(inputxml, arch='s390x',
                proc_cpuinfo=os.path.abspath('s390-guest.cpuinfo.txt'))
        self.assertEquals(expected, out)

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
