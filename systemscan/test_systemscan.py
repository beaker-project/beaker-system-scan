#!/usr/bin/python
import unittest
import json
import main

class PushInventoryTest(unittest.TestCase):

    def setUp(self):
        # Dumping 500 lines of xml directly into a unit test is not ok
        inputxml = open("./test_systemscan_xml").read()
        self.out = main.read_inventory(inputxml)

    def test_read_inventory_devices(self):
        with open('expected_devices.json') as f:
           devicelist = json.loads(f.read())
        for device in devicelist:
            self.assertTrue(device in self.out['Devices'], "Device missing, "
                            "or incorrectly reported: %s" % device['description'])

    def test_read_inventory_cpu(self):
        # Most cpu details are taken straight from proc, not the lshw xml
        # and so are not covered by this test

        flags = ['x86-64', 'fpu', 'fpu_exception', 'wp', 'vme', 'de', 'pse', 'tsc', 
                 'msr', 'pae', 'mce', 'cx8', 'apic', 'sep', 'mtrr', 'pge', 'mca', 
                 'cmov', 'pat', 'pse36', 'clflush', 'dts', 'acpi', 'mmx', 'fxsr', 
                 'sse', 'sse2', 'ss', 'ht', 'tm', 'pbe', 'syscall', 'nx', 'rdtscp', 
                 'constant_tsc', 'arch_perfmon', 'pebs', 'bts', 'rep_good', 'nopl', 
                 'xtopology', 'nonstop_tsc', 'aperfmperf', 'eagerfpu', 'pni', 'pclmulqdq', 
                 'dtes64', 'monitor', 'ds_cpl', 'vmx', 'smx', 'est', 'tm2', 'ssse3', 'cx16', 
                 'xtpr', 'pdcm', 'pcid', 'sse4_1', 'sse4_2', 'x2apic', 'popcnt', 
                 'tsc_deadline_timer', 'aes', 'xsave', 'avx', 'f16c', 'rdrand', 'lahf_lm', 
                 'ida', 'arat', 'epb', 'xsaveopt', 'pln', 'pts', 'dtherm', 'tpr_shadow', 'vnmi', 
                 'flexpriority', 'ept', 'vpid', 'fsgsbase', 'smep', 'erms', 'cpufreq']

        arch = 'x86-64'
        vendor = 'Intel Corp.'
        modelname = 'Core i7 (None)'
        self.assertEqual(arch, self.out['Arch'][0], "Expected %s for Arch, got %s" % (arch, self.out['Arch'][0]))
        self.assertEqual(vendor, self.out['Cpu']['vendor'], "Expected %s for Cpu vendor, got %s" % (vendor, self.out['Cpu']['vendor']))
        self.assertEqual(modelname, self.out['Cpu']['modelName'], "Expected %s for Cpu model, got %s" % (modelname, self.out['Cpu']['modelName']))
        for flag in self.out['Cpu']['CpuFlags']:
            self.assertTrue(flag in flags, "Flag missing from CpuFlags")

if __name__ == "__main__":
    unittest.main()
