from collections import defaultdict, Sequence, Sized, Iterable
import inspect
import wrapt
from cytoolz import curry
from numpy import ndarray

from .exceptions import UndefinedOperatorError, DifferentLengthError
from .exceptions import ExpectedTypeError, ShapeMismatchError
from .exceptions import ConstraintError


def equal_length(*args):
    '''Check that a tuple of arguments has the same length.
    '''
    for i, arg in enumerate(args):
        if not isinstance(arg, Sized):
            raise ExpectedTypeError(arg, ['Sized'])
        if i >= 1 and len(arg) != len(args[0]):
            raise DifferentLengthError(args, arg_tuple, arg)


@curry
def has_shape(shape, arg_id, args, kwargs):
    '''Check that a particular argument is an array with a given shape. The
    shape may contain string attributes, which will be fetched from arg0 to
    the function (usually self).
    '''
    self = args[0]
    arg = args[arg_id]
    if not hasattr(arg, 'shape'):
        raise ExpectedTypeError(arg, ['array'])
    shape_values = []
    for dim in shape:
        if not isinstance(dim, int):
            dim = getattr(self, dim, None)
        shape_values.append(dim)
    if len(shape) != len(arg.shape):
        raise ShapeMismatchError(arg.shape, tuple(shape_values), shape)
    for i, dim in enumerate(shape_values):
        # Allow underspecified dimensions
        if dim is not None and arg.shape[i] != dim:
            raise ShapeMismatchError(arg.shape, shape_values, shape)


def is_sequence(arg_id, args, kwargs):
    arg = args[arg_id]
    if not isinstance(arg, Iterable):
        raise ExpectedTypeError(arg, ['iterable'])


def is_float(arg_id, args, func_kwargs, **kwargs):
    arg = args[arg_id]
    if not isinstance(arg, float):
        raise ExpectedTypeError(arg, ['float'])
    if 'min' in kwargs and arg < kwargs['min']:
        raise ValueError("%s < min %s" % (arg, kwargs['min']))
    if 'max' in kwargs and arg > kwargs['max']:
        raise ValueError("%s > max %s" % (arg, kwargs['min']))


def is_array(arg_id, args, func_kwargs, **kwargs):
    arg = args[arg_id]
    if not isinstance(arg, ndarray):
        raise ExpectedTypeError(arg, ['ndarray'])


def operator_is_defined(op):
    @wrapt.decorator
    def checker(wrapped, instance, args, kwargs):
        if instance is None:
            instance = args[0]
        if instance is None:
            raise ExpectedTypeError(instance, ['Model'])
        if op not in instance._operators:
            raise UndefinedOperatorError(op, instance, args[0], instance._operators)
        else:
            return wrapped(*args, **kwargs)
    return checker


def arg(arg_id, *constraints):
    @wrapt.decorator
    def checked_function(wrapped, instance, args, kwargs):
        if not hasattr(wrapped, 'checks'):
            return wrapped(*args, **kwargs)
        if instance is not None:
            fix_args = [instance] + list(args)
        else:
            fix_args = list(args)
        for arg_id, checks in wrapped.checks.items():
            for check in checks:
                check(arg_id, fix_args, kwargs)
        return wrapped(*args, **kwargs)

    def arg_check_adder(func):
        if hasattr(func, 'checks'):
            func.checks.setdefault(arg_id, []).extend(constraints)
            return func
        else:
            wrapped = checked_function(func)
            wrapped.checks = {arg_id: list(constraints)}
            return wrapped
    return arg_check_adder


def args(*constraints):
    @wrapt.decorator
    def arg_check_adder(wrapped, instance, args, kwargs):
        for check in constraints:
            check(args)
        return wrapped(*args, **kwargs)
    return arg_check_adder
