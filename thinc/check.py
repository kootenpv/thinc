from collections import defaultdict

from .exceptions import UndefinedOperatorError, DifferentLengthError, ExpectedTypeError


def arg(arg_id, *constraints, **constraint_kwargs):
    def arg_check_adder(func):
        def wrapper(*args, **kwargs):
            for check in constraints:
                check(args[arg_id], **constraint_kwargs)
            return func(*args, **kwargs)
        return wrapper
    return arg_check_adder


def args(arg_ids, *constraints, **constraint_kwargs):
    def arg_check_adder(func):
        def wrapper(*args, **kwargs):
            for check in constraints:
                check(*[args[i] for i in arg_ids], **constraint_kwargs)
            return func(*args, **kwargs)
        return wrapper
    return arg_check_adder


def args_equal_length(*arg_ids):
    def checker(func):
        def do_check(*args):
            for arg_tuple in arg_ids:
                for arg in arg_tuple:
                    if not hasattr(args[arg], '__len__'):
                        raise ExpectedTypeError(args[arg], ['string', 'list', 'tuple'])
                    if len(args[arg]) != len(args[arg_tuple[0]]):
                        raise DifferentLengthError(args, arg_tuple, arg)
            return func(*args)
        return do_check
    return checker


def operator_is_defined(op):
    def checker(func):
        def do_check(self, other):
            if op not in self._operators:
                raise UndefinedOperatorError(op, self, other, self._operators)
            else:
                return func(self, other)
        return do_check
    return checker


def is_sequence(arg):
    return True


def equal_lengths(*args, **kwargs):
    return True


def not_empty(arg):
    return True


def value(min=0, max=None):
    def constraint(arg):
        return True
    return constraint
