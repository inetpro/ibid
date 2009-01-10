import re
from random import random, randint
from subprocess import Popen, PIPE

import ibid
from ibid.plugins import Processor, match

help = {}

help['retest'] = 'Checks whether a regular expression matches a given string.'
class ReTest(Processor):
    """does <pattern> match <string>"""
    feature = 'retest'

    @match('^does\s+(.+?)\s+match\s+(.+?)$')
    def retest(self, event, regex, string):
        event.addresponse(re.search(regex, string) and 'Yes' or 'No')

help['random'] = 'Generates random numbers.'
class Random(Processor):
    """random [ <max> | <min> <max> ]"""
    feature = 'random'

    @match('^rand(?:om)?(?:\s+(\d+)(?:\s+(\d+))?)?$')
    def random(self, event, begin, end):
        if not begin and not end:
            event.addresponse(str(random()))
        else:
            begin = int(begin)
            end = end and int(end) or 0
            event.addresponse(str(randint(min(begin,end), max(begin,end))))

bases = {   'bin': (lambda x: int(x, 2), lambda x: "".join(map(lambda y:str((x>>y)&1), range(8-1, -1, -1)))),
            'hex': (lambda x: int(x, 6), hex),
            'oct': (lambda x: int(x, 8), oct),
            'dec': (lambda x: int(x, 10), lambda x: x),
            'ascii': (ord, chr),
        }
help['base'] = 'Converts between numeric bases as well as ASCII.'
class Base(Processor):
    """convert <num> from <base> to <base>"""
    feature = 'base'

    @match(r'^convert\s+(\S+)\s+(?:from\s+)?(%s)\s+(?:to\s+)?(%s)$' % ('|'.join(bases.keys()), '|'.join(bases.keys())))
    def base(self, event, number, frm, to):
        number = bases[frm.lower()][0](number)
        number = bases[to.lower()][1](number)
        event.addresponse(str(number))

unit_names =    {   'fahrenheit': 'degF',
                    'celsius': 'degC',
                }
help['units'] = 'Converts values between various units.'
class Units(Processor):
    """convert [<value>] <unit> to <unit>"""
    feature = 'units'
    units = 'units'

    @match(r'^convert\s+([0-9.]+)?\s*(.+?)\s+(?:to\s+)?(.+?)$')
    def convert(self, event, value, frm, to):
        if frm.lower() in unit_names:
            frm = unit_names[frm.lower()]
        if to in unit_names:
            to = unit_names[to.lower()]
        if value:
            frm = '%s %s' % (value, frm)

        units = Popen([self.units, '--verbose', frm, to], stdout=PIPE, stderr=PIPE)
        output, error = units.communicate()
        code = units.wait()

        if code == 0:
            event.addresponse(output.splitlines()[0].strip())

# vi: set et sta sw=4 ts=4: