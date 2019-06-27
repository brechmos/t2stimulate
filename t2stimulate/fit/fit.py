from collections import namedtuple

import numpy as np
from scipy import optimize

from ..simulate.simulate import stimulate

Component = namedtuple('Component', 'pd t2 t1')


def list2Components(thelist):
    components = []
    for ii in np.arange(0, len(thelist), 3):
        components.append(Component(thelist[ii], thelist[ii + 1], thelist[ii + 2]))
    return components


def create_curve(te, components, b1):
    curve = np.zeros(te.shape)
    tau = te[2] - te[1]

    for component in components:
        curve = curve + component.pd * stimulate(alpha=b1, num_echoes=len(te), T1=component.t1, T2=component.t2,
                                                 tau=tau)

    return curve


def func(x, te, decay):
    # Convert components back
    components = list2Components(x[:-1])
    b1 = x[-1]

    print('diff is {}'.format(np.sqrt(np.sum((decay - create_curve(te, components, b1))**2))))
    return decay - create_curve(te, components, b1)


def fit(te, decay, components_initital, b1_initial):
    """

    Parameters
    ----------
    te: decay cruve (ms)
    decay:
    components_intital: (pd_0, t2_0, t1_0)
    components_bounds: ((pd_lower, pd_upper), (t2_lower, t2_upper), (t1_lower, t1_upper), ...)
    b1_initial

    Returns
    -------

    """

    # Convert the components_initial and b1_initial to an x0 vector.
    x0 = []
    x_lower = []
    x_upper = []
    for ci in components_initital:
        x0.extend((ci.pd, ci.t2, ci.t1))
        x_lower.extend([0, 0, 0])
        x_upper.extend([2000, 1000, 2000])
    x0.append(b1_initial)
    x_lower.append(np.pi/6)
    x_upper.append(np.pi)

    print('x_lower {}   x_upper {}'.format(x_lower, x_upper))

    # Fit the data
    results = optimize.least_squares(func, x0, bounds=(x_lower, x_upper), args=(te, decay,))
    x = results.x
    print(results)

    # Convert components back
    components = list2Components(x[:-1])
    b1 = x[-1]

    return components, b1
