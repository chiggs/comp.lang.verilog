"""
Simple testbench for a code snippet from comp.lang.verilog
"""

import random
import itertools

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ReadOnly
from cocotb.result import TestFailure
from cocotb.regression import TestFactory


# Data generators

def random_data(iterations=1000, bits=16, samples=5):
    """Random data"""
    for i in xrange(iterations):
        yield [random.getrandbits(bits) for s in range(samples)]


def corner_cases(bits=16):
    """Some specific corner cases"""
    cases = [[0,         1,         0,         2**bits-1, 2**bits-2],
             [1,         1,         1,         0,         0],
             [2**bits-1, 2**bits-2, 2**bits-3, 2**bits-4, 2**bits/2]]
    for case in cases:
        for variation in itertools.permutations(case):
            yield variation


# Main test function

@cocotb.coroutine
def run_test(dut, data_generator=random_data, delay_cycles=2):
    """
    Send data through the DUT and check it is sorted out output
    """
    cocotb.fork(Clock(dut.clk, 100).start())

    # Don't check until valid output
    expected = [None] * delay_cycles

    for index, values in enumerate(data_generator(bits=len(dut.in1))):
        expected.append(sorted(values))

        yield RisingEdge(dut.clk)
        dut.in1 = values[0]
        dut.in2 = values[1]
        dut.in3 = values[2]
        dut.in4 = values[3]
        dut.in5 = values[4]

        yield ReadOnly()
        expect = expected.pop(0)

        if expect is None: continue


        got = [int(dut.out5), int(dut.out4), int(dut.out3),
               int(dut.out2), int(dut.out1)]

        if got != expect:
            dut.log.error('Expected %s' % expect)
            dut.log.error('Got %s' % got)
            raise TestFailure("Output didn't match")

    dut.log.info('Sucessfully sent %d cycles of data' % (index + 1))

# Generate permutations of the test
tests = TestFactory(run_test)
tests.add_option('data_generator', [random_data, corner_cases])
tests.generate_tests()
