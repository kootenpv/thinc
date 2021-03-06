from __future__ import print_function
import pytest

from ...neural.vec2vec import Model, ReLu, Softmax
from ...neural._classes.feed_forward import FeedForward
from ...neural._classes.batchnorm import BatchNorm
from ...neural.ops import NumpyOps
from ...api import clone, chain
from ...loss import categorical_crossentropy

from ...extra import datasets

@pytest.fixture(scope='module')
def mnist():
    train_data, dev_data, _ = datasets.mnist()
    train_X, train_y = NumpyOps().unzip(train_data)
    dev_X, dev_y = NumpyOps().unzip(dev_data)
    return (train_X[:1000], train_y[:1000]), (dev_X, dev_y)


@pytest.fixture(scope='module')
def train_X(mnist):
    (train_X, train_y), (dev_X, dev_y) = mnist
    return train_X


@pytest.fixture(scope='module')
def train_y(mnist):
    (train_X, train_y), (dev_X, dev_y) = mnist
    return train_y


@pytest.fixture(scope='module')
def dev_X(mnist):
    (train_X, train_y), (dev_X, dev_y) = mnist
    return dev_X


@pytest.fixture(scope='module')
def dev_y(mnist):
    (train_X, train_y), (dev_X, dev_y) = mnist
    return dev_y


def create_relu_softmax(depth, width):
    with Model.define_operators({'*': clone, '>>': chain}):
        model = ReLu(width, 784) >> Softmax(10, width)
    return model


def create_relu_batchnorm_softmax(depth, width):
    with Model.define_operators({'*': clone, '>>': chain}):
        model = BatchNorm(ReLu(width, 784)) >> Softmax(10, width)
    return model

@pytest.fixture(params=[
    create_relu_softmax,
    create_relu_batchnorm_softmax])
def create_model(request):
    return request.param


@pytest.mark.parametrize(('depth', 'width', 'nb_epoch'), [(2, 8, 5)])
def test_small_end_to_end(depth, width, nb_epoch,
        create_model,
        train_X, train_y, dev_X, dev_y):
    model = create_model(depth, width)
    assert isinstance(model, FeedForward)
    losses = []
    with model.begin_training(train_X, train_y) as (trainer, optimizer):
        trainer.each_epoch.append(lambda: print(model.evaluate(dev_X, dev_y)))
        trainer.nb_epoch = nb_epoch
        for X, y in trainer.iterate(train_X, train_y):
            X = model.ops.asarray(X)
            y = model.ops.asarray(y)
            yh, backprop = model.begin_update(X, drop=trainer.dropout)
            d_loss, loss = categorical_crossentropy(yh, y)
            backprop(d_loss, optimizer)
            losses.append(loss)
    assert losses[-1] < losses[0]
