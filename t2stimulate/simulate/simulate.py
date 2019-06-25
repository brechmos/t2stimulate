import numpy as np


def _t1relax(B, tau, T1):
    Bcopy = B.copy()
    indices = np.r_[2:len(B):4, 3:len(B):4]
    Bcopy[indices] = Bcopy[indices] * np.exp(-tau / T1)
    return Bcopy


def _t2relax(B, tau, T2):
    Bcopy = B.copy()
    indices = np.r_[0:len(B):4, 1:len(B):4]
    Bcopy[indices] = Bcopy[indices] * np.exp(-tau / T2)
    return Bcopy


def _evolution(B):
    Bnew = B.copy()

    N = len(B)
    Bnew[4:N:4] = B[0:N - 4:4]
    Bnew[0] = B[1]
    Bnew[1:N - 4:4] = B[5:N:4]

    return Bnew


def _create_Tp(alpha):
    jay = complex(0, 1)

    # Precalculate rotation matrix Tone for one substate block
    Tone = np.array([[(np.cos(alpha / 2)) ** 2, (np.sin(alpha / 2)) ** 2, -jay * np.sin(alpha), 0],
                     [(np.sin(alpha / 2)) ** 2, (np.cos(alpha / 2)) ** 2, 0, jay * np.sin(alpha)],
                     [(-jay) * 1 / 2 * np.sin(alpha), (jay) * 1 / 2 * np.sin(alpha), np.cos(alpha), 0],
                     [(-jay) * 1 / 2 * np.sin(alpha), (jay) * 1 / 2 * np.sin(alpha), 0, np.cos(alpha)]])

    return Tone


def stimulate(alpha, num_echoes, T1, T2, tau):
    i = complex(0, 1)

    # vector to be output, should be floating point not complex
    decay = np.zeros((num_echoes,))

    B = np.zeros((num_echoes * 4, 1), dtype=complex)
    B[0] = i

    Tp = np.kron(np.eye(num_echoes), _create_Tp(alpha))

    B = _t2relax(B, tau, T2)
    B = _t1relax(B, tau, T1)

    for echo in np.arange(num_echoes):
        B = np.dot(Tp, B)

        decay[echo] = np.abs(B[1]) * np.exp(-tau / T2)

        B = _t2relax(B, 2 * tau, T2)
        B = _t1relax(B, 2 * tau, T1)
        B = _evolution(B)

    return decay
