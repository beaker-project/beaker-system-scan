
try:
    import json
except ImportError:
    import simplejson as json

import lxml.etree
import sys
from systemscan import main
import os
from glob import glob
import pytest


def assert_inventory_matches(expected, actual):
    # TODO FIXME cannot test 'Hypervisor' currently because it depends on 
    # the output of the hvm_detect program, which will always return 
    # a value based on the machine running the tests -- it does not look 
    # in the parsed XML from lshw, unlike everything else. So it's always 
    # going to be wrong here in the tests.
    del expected['Hypervisor']
    del actual['Hypervisor']

    # Also cannot test 'Numa' for the same reason. It comes from /sys on the 
    # build machine, and not from the lshw output.
    del expected['Numa']
    del actual['Numa']

    expected_devices = expected.pop('Devices')
    actual_devices = actual.pop('Devices')
    assert expected_devices == actual_devices

    expected_disks = expected.pop('Disk')['Disks']
    actual_disks = actual.pop('Disk')['Disks']
    assert expected_disks == actual_disks

    expected_cpu = expected.pop('Cpu')
    actual_cpu = actual.pop('Cpu')
    # CpuFlags is a list but the order is irrelevant
    expected_cpuflags = expected_cpu.pop('CpuFlags')
    actual_cpuflags = actual_cpu.pop('CpuFlags')
    assert sorted(expected_cpuflags) == sorted(actual_cpuflags)
    assert expected_cpu == actual_cpu

    assert expected == actual


def read_inventory_for_sample(sample):
    sample_dir = os.path.join(os.path.dirname(__file__), 'samples', sample)
    input_xml = lxml.etree.parse(os.path.join(sample_dir, 'input.xml'))
    cpuinfo_path = os.path.abspath(os.path.join(sample_dir, 'cpuinfo.txt'))
    arch = open(os.path.join(sample_dir, 'arch')).read().strip()
    return main.read_inventory(input_xml, arch=arch, proc_cpuinfo=cpuinfo_path)


@pytest.mark.parametrize('sample',
                         os.listdir(os.path.join(os.path.dirname(__file__), 'samples')))
def test_sample(sample):
    out = read_inventory_for_sample(sample)
    sample_dir = os.path.join(os.path.dirname(__file__), 'samples', sample)
    expected = json.load(open(os.path.join(sample_dir, 'expected.json')))
    assert_inventory_matches(expected, out)


# https://bugzilla.redhat.com/show_bug.cgi?id=1249460
def test_zero_values_are_excluded_from_USBID_key():
    inv = read_inventory_for_sample('hp-rx1620')
    legacy = main.legacy_inventory(inv)
    assert legacy['USBID'] == []


# https://bugzilla.redhat.com/show_bug.cgi?id=1249466
def test_diskspace_key_value():
    inv = read_inventory_for_sample('dell-pe2550')
    # The bug is only reproduced when a system has multiple disks whose 
    # size is slightly less than a whole number of megabytes:
    assert len(inv['Disk']['Disks']) == 4
    assert inv['Disk']['Disks'][0]['size'] == '36420075008'
    assert inv['Disk']['Disks'][1]['size'] == '36420075008'
    assert inv['Disk']['Disks'][2]['size'] == '36420075008'
    assert inv['Disk']['Disks'][3]['size'] == '36420075008'
    legacy = main.legacy_inventory(inv)
    assert legacy['DISKSPACE'] == 138931


def test_map_32bit_archs():
    sample_dir = os.path.join(os.path.dirname(__file__), 'samples', 'hp-z420')
    input_xml = lxml.etree.parse(os.path.join(sample_dir, 'input.xml'))
    cpuinfo_path = os.path.abspath(os.path.join(sample_dir, 'cpuinfo.txt'))
    i686 = main.read_inventory(input_xml, arch='i686', proc_cpuinfo=cpuinfo_path)
    assert i686['Arch'][0] == 'i386'
