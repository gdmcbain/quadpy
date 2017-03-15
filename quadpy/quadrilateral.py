# -*- coding: utf-8 -*-
#
from . import line_segment
from . import helpers

import math
import numpy


def show(
        scheme,
        quad=numpy.array([[0, 0], [1, 0], [1, 1], [0, 1]]),
        show_axes=False
        ):
    '''Shows the quadrature points on a given quad. The area of the disks
    around the points coincides with their weights.
    '''
    from matplotlib import pyplot as plt

    plt.plot(quad[:, 0], quad[:, 1], '-k')
    plt.plot(
        [quad[-1, 0], quad[0, 0]],
        [quad[-1, 1], quad[0, 1]],
        '-k'
        )

    plt.axis('equal')

    if not show_axes:
        plt.gca().set_axis_off()

    xi = scheme.points[:, 0]
    eta = scheme.points[:, 1]
    transformed_pts = \
        + numpy.outer(0.25 * (1.0 - xi)*(1.0 - eta), quad[0]) \
        + numpy.outer(0.25 * (1.0 + xi)*(1.0 - eta), quad[1]) \
        + numpy.outer(0.25 * (1.0 + xi)*(1.0 + eta), quad[2]) \
        + numpy.outer(0.25 * (1.0 - xi)*(1.0 + eta), quad[3])

    vol = integrate(lambda x: numpy.ones(1), quad, Stroud(1))
    helpers.plot_disks(
        plt, transformed_pts, scheme.weights, vol
        )
    plt.show()
    return


def integrate(f, quad, scheme):
    xi = scheme.points.T
    x = \
        + numpy.outer(quad[0], 0.25*(1.0-xi[0])*(1.0-xi[1])) \
        + numpy.outer(quad[1], 0.25*(1.0+xi[0])*(1.0-xi[1])) \
        + numpy.outer(quad[2], 0.25*(1.0+xi[0])*(1.0+xi[1])) \
        + numpy.outer(quad[3], 0.25*(1.0-xi[0])*(1.0+xi[1]))

    J0 = \
        - numpy.outer(quad[0], 0.25*(1-xi[1])) \
        + numpy.outer(quad[1], 0.25*(1-xi[1])) \
        + numpy.outer(quad[2], 0.25*(1+xi[1])) \
        - numpy.outer(quad[3], 0.25*(1+xi[1]))
    J1 = \
        - numpy.outer(quad[0], 0.25*(1-xi[0])) \
        - numpy.outer(quad[1], 0.25*(1+xi[0])) \
        + numpy.outer(quad[2], 0.25*(1+xi[0])) \
        + numpy.outer(quad[3], 0.25*(1-xi[0]))
    det = J0[0]*J1[1] - J1[0]*J0[1]

    return math.fsum(scheme.weights * f(x).T * abs(det))


class From1d(object):
    def __init__(self, scheme1d):
        self.weights = numpy.outer(
            scheme1d.weights, scheme1d.weights
            ).flatten()
        self.points = numpy.dstack(numpy.meshgrid(
            scheme1d.points, scheme1d.points
            )).reshape(-1, 2)
        self.degree = scheme1d.degree
        return


class Stroud(object):
    '''
    Arthur Stroud,
    Approximate Calculation of Multiple Integrals,
    Prentice Hall, 1971.

    <https://people.sc.fsu.edu/~jburkardt/m_src/stroud/square_unit_set.m>
    '''
    def __init__(self, index):
        if index == 1:
            self.weights = numpy.array([
                4.0,
                ])
            self.points = numpy.array([
                [0.0, 0.0]
                ])
            self.degree = 1
        elif index == 2:
            self.weights = numpy.ones(4)
            self.points = self._symm_s(1.0/numpy.sqrt(3.0))
            self.degree = 3
        elif index == 3:
            self.weights = numpy.concatenate([
                64.0/81.0 * numpy.ones(1),
                25.0/81.0 * numpy.ones(4),
                40.0/81.0 * numpy.ones(4),
                ])
            self.points = numpy.concatenate([
                numpy.array([[0.0, 0.0]]),
                self._symm_s(numpy.sqrt(0.6)),
                self._symm_r_0(numpy.sqrt(0.6)),
                ])
            self.degree = 5
        elif index == 4:
            # Stroud number C2:7-1.
            r = numpy.sqrt(6.0 / 7.0)
            c = 3.0 * numpy.sqrt(583.0)
            s = numpy.sqrt((114.0 - c) / 287.0)
            t = numpy.sqrt((114.0 + c) / 287.0)
            w1 = 4.0 * 49.0 / 810.0
            w2 = 4.0 * (178981.0 + 923.0 * c) / 1888920.0
            w3 = 4.0 * (178981.0 - 923.0 * c) / 1888920.0
            #
            self.weights = numpy.concatenate([
                w1 * numpy.ones(4),
                w2 * numpy.ones(4),
                w3 * numpy.ones(4),
                ])
            self.points = numpy.concatenate([
                self._symm_r_0(r),
                self._symm_s(s),
                self._symm_s(t),
                ])
            self.degree = 7
        elif index == 5:
            # Stroud number C2:7-3.
            r = numpy.sqrt(12.0 / 35.0)
            c = 3.0 * numpy.sqrt(186.0)
            s = numpy.sqrt((93.0 + c) / 155.0)
            t = numpy.sqrt((93.0 - c) / 155.0)
            w1 = 8.0 / 162.0
            w2 = 98.0 / 162.0
            w3 = 31.0 / 162.0
            self.weights = numpy.concatenate([
                w1 * numpy.ones(1),
                w2 * numpy.ones(4),
                w3 * numpy.ones(8),
                ])
            self.points = numpy.concatenate([
                numpy.array([[0.0, 0.0]]),
                self._symm_r_0(r),
                self._symm_s_t(s, t),
                ])
            self.degree = 7
        elif index == 6:
            scheme1d = line_segment.GaussLegendre(8)
            self.weights = numpy.outer(
                scheme1d.weights, scheme1d.weights
                ).flatten()
            self.points = numpy.dstack(numpy.meshgrid(
                scheme1d.points, scheme1d.points
                )).reshape(-1, 2)
            assert len(self.points) == 64
            self.degree = 15
        else:
            raise ValueError('Illegal Stroud index')

        return

    def _symm_r_0(self, r):
        return numpy.array([
            [+r, 0.0],
            [-r, 0.0],
            [0.0, +r],
            [0.0, -r],
            ])

    def _symm_s(self, s):
        return numpy.array([
            [+s, +s],
            [-s, +s],
            [+s, -s],
            [-s, -s],
            ])

    def _symm_s_t(self, s, t):
        return numpy.array([
            [+s, +t],
            [-s, +t],
            [+s, -t],
            [-s, -t],
            [+t, +s],
            [-t, +s],
            [+t, -s],
            [-t, -s],
            ])