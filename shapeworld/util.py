from __future__ import division
from collections import Counter, namedtuple
from itertools import chain, combinations
import json
from math import ceil, floor, sqrt, trunc
from operator import __truediv__
import os
from random import random, uniform
import tarfile
import time
import zipfile


def parse_int_with_factor(string):
    assert string
    if len(string) < 2:
        return int(string)
    elif string[-1] == 'k':
        return int(string[:-1]) * 1000
    elif string[-1] == 'M':
        return int(string[:-1]) * 1000000
    elif string[-2:] == 'Ki':
        return int(string[:-2]) * 1024
    elif string[-2:] == 'Mi':
        return int(string[:-2]) * 1048576
    else:
        return int(string)


def parse_config(string):
    assert string
    if string.lower() in ('none', 'null'):
        return None
    elif string[0] == '{':
        assert string[-1] == '}'
        if '\'' in string and '\"' not in string:
            string = string.replace('\'', '\"')
        if '=' in string and ':' not in string:
            string = string.replace('=', ':')
        return json.loads(string)
    else:
        return string


def powerset(values, min_num=None, max_num=None):
    values = list(values)
    min_num = min_num or 0
    max_num = max_num or len(values)
    return chain.from_iterable(combinations(values, num) for num in range(min_num, max_num + 1))


# partial_order is dict: x -> set({>x})
def toposort(partial_order):
    result = []
    smaller = Counter(y for ys in partial_order.values() for y in ys)
    smallest = [x for x in partial_order if not smaller[x]]
    while smallest:
        x = smallest.pop()
        result.append(x)
        for y in partial_order[x]:
            smaller[y] -= 1
            if not smaller[y]:
                smallest.append(y)
    assert not list(smaller.elements())
    return result


def cumulative_distribution(values):
    if isinstance(values, int):
        assert values > 0
        return [n / values for n in range(1, values + 1)]
    elif all(isinstance(x, float) or isinstance(x, int) for x in values):
        assert all(x >= 0.0 for x in values)
        denominator = sum(values)
        prob = 0.0
        cdf = []
        for x in values:
            prob += x
            cdf.append(prob / denominator)
        return cdf
    else:
        assert False


def sample(cumulative_distribution, items=None):
    sample = random()
    if items:
        for item, prob in zip(items, cumulative_distribution):
            if sample < prob:
                return item
    else:
        for index, prob in enumerate(cumulative_distribution):
            if sample < prob:
                return index


PointTuple = namedtuple('PointTuple', ('x', 'y'))


class Point(PointTuple):

    def __new__(cls, x, y):
        assert isinstance(x, float) or isinstance(x, int) or isinstance(x, bool) or isinstance(x, str)
        assert isinstance(y, float) or isinstance(y, int) or isinstance(y, bool) or isinstance(y, str)
        if isinstance(x, str):
            x = float(x)
        if isinstance(y, str):
            y = float(y)
        return super(Point, cls).__new__(cls, x, y)

    def __str__(self):
        return '({}/{})'.format(self.x, self.y)

    def model(self):
        return {'x': self.x, 'y': self.y}

    def __eq__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return self.x == other.x and self.y == other.y
        else:
            return self.x == other and self.y == other

    def __ne__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return self.x != other.x or self.y != other.y
        else:
            return self.x != other or self.y != other

    def __lt__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return self.x < other.x and self.y < other.y
        else:
            return self.x < other and self.y < other

    def __gt__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return self.x > other.x and self.y > other.y
        else:
            return self.x > other and self.y > other

    def __le__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return self.x <= other.x and self.y <= other.y
        else:
            return self.x <= other and self.y <= other

    def __ge__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return self.x >= other.x and self.y >= other.y
        else:
            return self.x >= other and self.y >= other

    def __pos__(self):
        return Point(self.x, self.y)

    def __neg__(self):
        return Point(-self.x, -self.y)

    def __add__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return Point(self.x + other.x, self.y + other.y)
        else:
            return Point(self.x + other, self.y + other)

    def __sub__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return Point(self.x - other.x, self.y - other.y)
        else:
            return Point(self.x - other, self.y - other)

    def __mul__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return Point(self.x * other.x, self.y * other.y)
        else:
            return Point(self.x * other, self.y * other)

    def __truediv__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return Point(__truediv__(self.x, other.x), __truediv__(self.y, other.y))
        else:
            return Point(__truediv__(self.x, other), __truediv__(self.y, other))

    def __floordiv__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return Point(self.x // other.x, self.y // other.y)
        else:
            return Point(self.x // other, self.y // other)

    def __div__(self, other):
        return self.__truediv__(other)

    def __mod__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return Point(self.x % other.x, self.y % other.y)
        else:
            return Point(self.x % other, self.y % other)

    def __divmod__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return Point(self.x // other.x, self.y // other.y), Point(self.x % other.x, self.y % other.y)
        else:
            return Point(self.x // other, self.y // other), Point(self.x % other, self.y % other)

    def __pow__(self, other, modulo=None):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if modulo is None:
            if isinstance(other, Point):
                return Point(self.x ** other.x, self.y ** other.y)
            else:
                return Point(self.x ** other, self.y ** other)
        else:
            if isinstance(other, Point):
                return Point(pow(self.x, other.x, modulo), pow(self.y, other.y, modulo))
            else:
                return Point(pow(self.x, other, modulo), pow(self.y, other, modulo))

    def __radd__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool)
        return Point(other + self.x, other + self.y)

    def __rsub__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool)
        return Point(other - self.x, other - self.y)

    def __rmul__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool)
        return Point(other * self.x, other * self.y)

    def __rtruediv__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool)
        return Point(__truediv__(other, self.x), __truediv__(other, self.y))

    def __rfloordiv__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool)
        return Point(other // self.x, other // self.y)

    def __rmod__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool)
        return Point(other % self.x, other % self.y)

    def __rdivmod__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool)
        return Point(other // self.x, other // self.y), Point(other % self.x, other % self.y)

    def __rpow__(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool)
        return Point(other ** self.x, other ** self.y)

    def __abs__(self):
        if isinstance(self.x, bool):
            return Point(self.x, self.y)
        else:
            return Point(abs(self.x), abs(self.y))

    def __round__(self, n=0):
        return Point(round(self.x, n), round(self.y, n))

    def __floor__(self):
        return Point(floor(self.x), floor(self.y))

    def __ceil__(self):
        return Point(ceil(self.x), ceil(self.y))

    def __trunc__(self):
        return Point(trunc(self.x), trunc(self.y))

    def square(self):
        return Point(self.x * self.x, self.y * self.y)

    def length(self):
        return sqrt(self.x * self.x + self.y * self.y)

    def positive(self):
        if isinstance(self.x, bool):
            return Point(self.x, self.y)
        elif isinstance(self.x, int):
            return Point(max(self.x, 0), max(self.y, 0))
        else:
            return Point(max(self.x, 0.0), max(self.y, 0.0))

    def min(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return Point(min(self.x, other.x), min(self.y, other.y))
        else:
            return Point(min(self.x, other), min(self.y, other))

    def max(self, other):
        assert isinstance(other, float) or isinstance(other, int) or isinstance(other, bool) or isinstance(other, Point)
        if isinstance(other, Point):
            return Point(max(self.x, other.x), max(self.y, other.y))
        else:
            return Point(max(self.x, other), max(self.y, other))

    def rotate(self, angle_sin, angle_cos):
        return Point(self.x * angle_cos - self.y * angle_sin, self.x * angle_sin + self.y * angle_cos)

    @staticmethod
    def range(start, end=None, size=None, step=None):
        assert isinstance(start, Point)
        assert end is None or isinstance(end, Point)
        assert size is None or isinstance(size, Point)
        if end is None:
            end = start.__ceil__()
            start = Point.izero
        else:
            start = start.__floor__()
            end = end.__ceil__()
        assert start <= end
        if size is None:
            for x in range(int(start.x), int(end.x)):
                for y in range(int(start.y), int(end.y)):
                    yield Point(x, y)
        else:
            for x in range(int(start.x), int(end.x)):
                for y in range(int(start.y), int(end.y)):
                    point = Point(x, y)
                    yield point, Point(x / size.x, y / size.y)

    @staticmethod
    def random_instance(topleft, bottomright):
        return Point(uniform(topleft.x, bottomright.x), uniform(topleft.y, bottomright.y))


Point.zero = Point(0.0, 0.0)
Point.one = Point(1.0, 1.0)
Point.half = Point(0.5, 0.5)

Point.izero = Point(0, 0)
Point.ione = Point(1, 1)
Point.right = Point(1, 0)
Point.top_right = Point(1, 1)
Point.top = Point(0, 1)
Point.top_left = Point(-1, 1)
Point.left = Point(-1, 0)
Point.bottom_left = Point(-1, -1)
Point.bottom = Point(0, -1)
Point.bottom_right = Point(1, -1)
Point.directions = (Point.right, Point.top, Point.left, Point.bottom)
Point.directions_ext = (Point.right, Point.top_right, Point.top, Point.top_left, Point.left, Point.bottom_left, Point.bottom, Point.bottom_right)


class Archive(object):

    def __init__(self, path, mode, archive=None):
        assert mode == 'r' or mode == 'w'
        assert archive in (None, 'zip', 'zip:none', 'zip:deflate', 'zip:bzip2', 'zip:lzma', 'tar', 'tar:none', 'tar:gzip', 'tar:bzip2', 'tar:lzma')
        self.archive = path
        self.mode = mode
        if not os.path.isdir('/tmp/shapeworld'):
            os.makedirs('/tmp/shapeworld')
        self.temp_directory = os.path.join('/tmp/shapeworld', str(time.time()))
        os.mkdir(self.temp_directory)
        if archive is None:
            self.archive_type = None
            if not os.path.isdir(self.archive):
                os.mkdir(self.archive)
        elif archive[:3] == 'zip':
            self.archive_type = 'zip'
            if len(archive) == 3:
                compression = zipfile.ZIP_DEFLATED
            elif archive[4:] == 'none':
                compression = zipfile.ZIP_STORED
            elif archive[4:] == 'deflate':
                compression = zipfile.ZIP_DEFLATED
            elif archive[4:] == 'bzip2':
                compression = zipfile.ZIP_BZIP2
            elif archive[4:] == 'lzma':
                compression = zipfile.ZIP_LZMA
            if not self.archive.endswith('.zip'):
                self.archive += '.zip'
            self.archive = zipfile.ZipFile(self.archive, mode, compression)
        elif archive[:3] == 'tar':
            self.archive_type = 'tar'
            if len(archive) == 3:
                mode += ':gz'
                extension = '.gz'
            elif archive[4:] == 'none':
                extension = ''
            elif archive[4:] == 'gzip':
                mode += ':gz'
                extension = '.gz'
            elif archive[4:] == 'bzip2':
                mode += ':bz2'
                extension = '.bz2'
            elif archive[4:] == 'lzma':
                mode += ':xz'
                extension = '.lzma'
            if not self.archive.endswith('.tar' + extension):
                self.archive += '.tar' + extension
            self.archive = tarfile.open(self.archive, mode)

    def close(self):
        if self.archive_type is not None:
            self.archive.close()
        os.rmdir(self.temp_directory)

    def __enter__(self):
        if self.mode == 'r':
            return self.read_file
        else:
            return self.write_file

    def __exit__(self, type, value, traceback):
        self.close()
        return False

    def read_file(self, filename, binary=False):
        if self.archive_type is None:
            filename = os.path.join(self.archive, filename)
            if not os.path.isfile(filename):
                return None
            with open(filename, 'rb' if binary else 'r') as filehandle:
                value = filehandle.read()
            return value
        elif self.archive_type == 'zip':
            try:
                fileinfo = self.archive.getinfo(filename)
            except KeyError:
                return None
            value = self.archive.read(fileinfo)
            if not binary:
                value = value.decode()
            return value
        elif self.archive_type == 'tar':
            try:
                fileinfo = self.archive.getmember(filename)
            except KeyError:
                return None
            self.archive.extract(member=fileinfo, path=self.temp_directory)
            filepath = os.path.join(self.temp_directory, filename)
            with open(filepath, 'rb' if binary else 'r') as filehandle:
                value = filehandle.read()
            os.remove(filepath)
            return value

    def write_file(self, filename, value, binary=False):
        if self.archive_type is None:
            filename = os.path.join(self.archive, filename)
            with open(filename, 'wb' if binary else 'w') as filehandle:
                filehandle.write(value)
        elif self.archive_type == 'zip':
            if binary:
                filepath = os.path.join(self.temp_directory, filename)
                with open(filepath, 'wb') as filehandle:
                    filehandle.write(value)
                self.archive.write(filepath, filename)
                os.remove(filepath)
            else:
                self.archive.writestr(filename, value)
        elif self.archive_type == 'tar':
            filepath = os.path.join(self.temp_directory, filename)
            with open(filepath, 'wb' if binary else 'w') as filehandle:
                filehandle.write(value)
            self.archive.add(filepath, filename)
            os.remove(filepath)
