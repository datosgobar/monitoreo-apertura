import csvvalidator

from csvvalidator import CSVValidator, datetime_string, enumeration

from monitoreo.apps.dashboard.models import IndicatorType
from monitoreo.apps.dashboard.models.indicators import AbstractIndicator

csvvalidator.basestring = str


class IndicatorValidatorGenerator:
    def __init__(self, model):
        indicator_names = IndicatorType.objects.all()\
            .values_list('nombre', flat=True)
        self.value_checks = [
            ('fecha', datetime_string('%Y-%m-%d')),
            ('indicador_tipo__nombre', enumeration(list(indicator_names))),
            ('indicador_valor', str),
        ]
        self.unique_checks = ('fecha',
                              'indicador_tipo__nombre', )
        if issubclass(model, AbstractIndicator):
            self.value_checks = self.value_checks + [
                ('jurisdiccion_id', str),
                ('jurisdiccion_nombre', str), ]
            self.unique_checks = self.unique_checks + ('jurisdiccion_id', )

        self.field_names = [check[0] for check in self.value_checks]

    def generate(self):
        validator = CSVValidator(self.field_names)
        validator.add_header_check()
        validator.add_record_length_check()
        for value, check in self.value_checks:
            validator.add_value_check(value, check)
        validator.add_unique_check(self.unique_checks)
        return validator


class ValidationError(ValueError):
    pass


def write_problems(problems, file, summarize=False, limit=0):
    """
    Write problems as restructured text to a file (or stdout/stderr).

    """
    write = file.write  # convenience variable
    write("""
=================
Validation Report
=================
""")
    counts = dict()  # store problem counts per problem code
    total = 0
    for i, problem in enumerate(problems):
        if limit and i >= limit:
            break  # bail out
        if total == 0 and not summarize:
            write("""
Problems
========
""")
        total += 1
        code = problem['code']
        if code in counts:
            counts[code] += 1
        else:
            counts[code] = 1
        if not summarize:
            ptitle = '\n%s - %s\n' % (problem['code'], problem['message'])
            write(ptitle)
            underline = '-' * len(ptitle.strip()) + '\n'
            write(underline)
            for problem_key in \
                    sorted(problem.keys() - {'code', 'message', 'context'}):
                write(':%s: %s\n' % (problem_key, problem[problem_key]))
            if 'context' in problem:
                context = problem['context']
                for context_key in sorted(context.keys()):
                    write(':%s: %s\n' % (context_key, context[context_key]))

    write("""
Summary
=======

Found %s%s problem%s in total.

""" % ('at least ' if limit else '', total, 's' if total != 1 else ''))
    for code in sorted(counts.keys()):
        write(':%s: %s\n' % (code, counts[code]))
    return total
