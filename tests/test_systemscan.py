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

    longMessage = True
    maxDiff = None

    def assert_inventory_matches(self, expected, actual):
        # TODO FIXME cannot test 'Hypervisor' currently because it depends on 
        # the output of the hvm_detect program, which will always return 
        # a value based on the machine running the tests -- it does not look 
        # in the parsed XML from lshw, unlike everything else. So it's always 
        # going to be wrong here in the tests.
        del expected['Hypervisor']
        del actual['Hypervisor']

        expected_devices = expected.pop('Devices')
        actual_devices = actual.pop('Devices')
        for i, device in enumerate(expected_devices):
            try:
                self.assertEquals(device, actual_devices[i])
            except IndexError:
                self.fail('Missing device %s' % device)

        expected_disks = expected.pop('Disk')['Disks']
        actual_disks = actual.pop('Disk')['Disks']
        for i, disk in enumerate(expected_disks):
            try:
                self.assertEquals(disk, actual_disks[i])
            except IndexError:
                self.fail('Missing disk %s' % disk)

        expected_cpuflags = expected['Cpu']['CpuFlags']
        actual_cpuflags = actual['Cpu']['CpuFlags']
        self.assertItemsEqual(expected_cpuflags, actual_cpuflags)

        for key in expected['Cpu']:
            self.assertEquals(expected['Cpu'][key], actual['Cpu'][key],
                    'Cpu %s should match' % key)

        for key in expected:
            self.assertEquals(expected[key], actual[key],
                    '%s should match' % key)

    def test_read_inventory_hp_z420(self):
        inputxml = lxml.etree.parse('hp-z420.xml')
        expected = json.load(open('hp-z420.expected.json'))
        out = main.read_inventory(inputxml, arch='x86_64',
                proc_cpuinfo=os.path.abspath('hp-z420.cpuinfo.txt'))
        self.assert_inventory_matches(expected, out)

    def test_read_inventory_dell_pe2550(self):
        inputxml = lxml.etree.parse('dell-pe2550.xml')
        expected = json.load(open('dell-pe2550.expected.json'))
        out = main.read_inventory(inputxml, arch='x86_64',
                proc_cpuinfo=os.path.abspath('dell-pe2550.cpuinfo.txt'))
        self.assert_inventory_matches(expected, out)

    def test_read_inventory_ia64(self):
        inputxml = lxml.etree.parse('hp-rx1620.xml')
        expected = json.load(open('hp-rx1620.expected.json'))
        out = main.read_inventory(inputxml, arch='ia64',
                proc_cpuinfo=os.path.abspath('hp-rx1620.cpuinfo.txt'))
        self.assert_inventory_matches(expected, out)

    # https://bugzilla.redhat.com/show_bug.cgi?id=1249460
    def test_zero_values_are_excluded_from_USBID_key(self):
        inputxml = lxml.etree.parse('hp-rx1620.xml')
        expected = json.load(open('hp-rx1620.expected.json'))
        inv = main.read_inventory(inputxml, arch='ia64',
                proc_cpuinfo=os.path.abspath('hp-rx1620.cpuinfo.txt'))
        legacy = main.legacy_inventory(inv)
        self.assertEquals(legacy['USBID'], [])

    def test_read_inventory_s390x(self):
        inputxml = lxml.etree.parse('s390-guest.xml')
        expected = json.load(open('s390-guest.expected.json'))
        out = main.read_inventory(inputxml, arch='s390x',
                proc_cpuinfo=os.path.abspath('s390-guest.cpuinfo.txt'))
        self.assert_inventory_matches(expected, out)

    # https://bugzilla.redhat.com/show_bug.cgi?id=1249466
    def test_diskspace_key_value(self):
        inputxml = lxml.etree.parse('dell-pe2550.xml')
        inv = main.read_inventory(inputxml, arch='x86_64',
                proc_cpuinfo=os.path.abspath('dell-pe2550.cpuinfo.txt'))
        # The bug is only reproduced when a system has multiple disks whose 
        # size is slightly less than a whole number of megabytes:
        self.assertEquals(len(inv['Disk']['Disks']), 4)
        self.assertEquals(inv['Disk']['Disks'][0]['size'], '36420075008')
        self.assertEquals(inv['Disk']['Disks'][1]['size'], '36420075008')
        self.assertEquals(inv['Disk']['Disks'][2]['size'], '36420075008')
        self.assertEquals(inv['Disk']['Disks'][3]['size'], '36420075008')
        legacy = main.legacy_inventory(inv)
        self.assertEquals(legacy['DISKSPACE'], 138931)

    def test_map_32bit_archs(self):
        inputxml = lxml.etree.parse('hp-z420.xml')
        i686 = main.read_inventory(inputxml, arch='i686',
                proc_cpuinfo=os.path.abspath('hp-z420.cpuinfo.txt'))
        self.assertEquals('i386', i686['Arch'][0])

    def test_read_inventory_aarch64(self):
        inputxml = lxml.etree.parse('apm-mustang.xml')
        expected = json.load(open('apm-mustang.expected.json'))
        out = main.read_inventory(inputxml, arch='aarch64',
                proc_cpuinfo=os.path.abspath('apm-mustang.cpuinfo.txt'))
        self.assert_inventory_matches(expected, out)

    def test_read_inventory_x86_kvm_guest(self):
        inputxml = lxml.etree.parse('x86-kvm-guest.xml')
        expected = json.load(open('x86-kvm-guest.expected.json'))
        out = main.read_inventory(inputxml, arch='x86_64',
                proc_cpuinfo=os.path.abspath('x86-kvm-guest.cpuinfo.txt'))
        self.assert_inventory_matches(expected, out)

if __name__ == "__main__":
    unittest.main()
