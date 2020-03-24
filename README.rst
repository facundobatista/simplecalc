What is simplecalc?
-------------------

A simple calculator, able to parse quite complex expressions::

    >>> from simplecalc import calc
    >>> calc("2 + 3.5")
    '5.5'
    >>> calc("2 * log(100)")
    '4'
    >>> calc("sin(pi / 2)")
    '1'
    >>> calc("3 * 5!")
    '360'
    >>> calc("3 * 5! + ceil(sqrt(123) / ln(10))")
    '368'
    >>> calc("3**e  * 5! + ceil(sqrt(123) * ln(10))")
    '2394.55888943'

Note that these expressions are NOT evaluated by eval() or anything like that,
so it should be safe to get the expressions from untrusted sources. Use at
your own risk, of course.

It can also be used as a script::

    $ simplecalc "3 * cos(pi)"
    -3


Project's history
-----------------

Code here comes from other internal Canonical's project, this part was 
opensourced in 2018:

    https://launchpad.net/simple-calc

I forked that to bring it to GitHub, migrate it to Python 3, shape it more
like a project (have a ``setup.py``, etc.), and do some releases.
