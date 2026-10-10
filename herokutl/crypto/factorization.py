"""
This module holds a fast Factorization class.
"""

from random import randint

from rsa.prime import miller_rabin_primality_testing


class Factorization:
    """
    Simple module to factorize large numbers really quickly.
    """

    @classmethod
    def factorize(cls, pq, max_steps=1_000_000):
        """
        Factorizes the given large integer.

        Implementation from https://comeoncodeon.wordpress.com/2010/09/18/pollard-rho-brent-integer-factorization/.

        :param pq: the prime pair pq.
        :return: a tuple containing the two factors p and q.
        """
        if pq < 4:
            raise ValueError("pq must be composite")
        if pq % 2 == 0:
            return 2, pq // 2

        # cryptg ships a Rust implementation of the same Pollard-Brent
        # algorithm; it is several times faster than pure Python and is
        # only ever needed during login / DC migration. However, some
        # inputs do not panic but loop forever while holding the GIL
        # (tiny composites such as 9, and some primes), so the fast
        # path is restricted to login-sized composites; everything
        # else goes straight to the pure Python implementation, which
        # always terminates.
        if pq >= 2 ** 32 and not miller_rabin_primality_testing(pq, 16):
            try:
                from cryptg import factorize_pq_pair
            except ImportError:
                pass
            else:
                try:
                    p, q = sorted(factorize_pq_pair(pq))
                except (KeyboardInterrupt, SystemExit):
                    raise
                except BaseException:
                    # Rust panics surface as BaseException (pyo3) and
                    # cannot be caught as Exception; the call is
                    # microseconds long
                    pass
                else:
                    if p * q == pq and 1 < p < q:
                        return p, q

        y, c, m = randint(1, pq - 1), randint(1, pq - 1), randint(1, pq - 1)
        g = r = q = 1
        x = ys = 0
        steps = 0

        while g == 1:
            x = y
            for i in range(r):
                steps += 1
                if steps > max_steps:
                    raise ValueError("Factorization work limit exceeded")
                y = (pow(y, 2, pq) + c) % pq

            k = 0
            while k < r and g == 1:
                ys = y
                for i in range(min(m, r - k)):
                    steps += 1
                    if steps > max_steps:
                        raise ValueError("Factorization work limit exceeded")
                    y = (pow(y, 2, pq) + c) % pq
                    q = q * (abs(x - y)) % pq

                g = cls.gcd(q, pq)
                k += m

            r *= 2

        if g == pq:
            while True:
                steps += 1
                if steps > max_steps:
                    raise ValueError("Factorization work limit exceeded")
                ys = (pow(ys, 2, pq) + c) % pq
                g = cls.gcd(abs(x - ys), pq)
                if g > 1:
                    break

        p, q = g, pq // g
        return (p, q) if p < q else (q, p)

    @staticmethod
    def gcd(a, b):
        """
        Calculates the Greatest Common Divisor.

        :param a: the first number.
        :param b: the second number.
        :return: GCD(a, b)
        """
        while b:
            a, b = b, a % b

        return a
