import numpy as np
import xarray as xr
import pandas as pd
import time


def daily_downsampler(da, freq='YS'):
    r"""Daily climate data downsampler

    Parameters
    ----------
    da : xarray.DataArray
    freq : string

    Returns
    -------
    xarray.DataArray


    Note
    ----

        Usage Example

            grouper = daily_downsampler(da_std, freq='YS')
            x2 = grouper.mean()

            # add time coords to x2 and change dimension tags to time
            time1 = daily_downsampler(da_std.time, freq=freq).first()
            x2.coords['time'] = ('tags', time1.values)
            x2 = x2.swap_dims({'tags': 'time'})
            x2 = x2.sortby('time')
    """

    # generate tags from da.time and freq
    if isinstance(da.time.values[0], np.datetime64):
        years = ['{:04d}'.format(y) for y in da.time.dt.year.values]
        months = ['{:02d}'.format(m) for m in da.time.dt.month.values]
    else:
        # cannot use year, month, season attributes, not available for all calendars ...
        years = ['{:04d}'.format(v.year) for v in da.time.values]
        months = ['{:02d}'.format(v.month) for v in da.time.values]
    seasons = ['DJF DJF MAM MAM MAM JJA JJA JJA SON SON SON DJF'.split()[int(m) - 1] for m in months]

    n_t = da.time.size
    if freq == 'YS':
        # year start frequency
        l_tags = years
    elif freq == 'MS':
        # month start frequency
        l_tags = [years[i] + months[i] for i in range(n_t)]
    elif freq == 'QS-DEC':
        # DJF, MAM, JJA, SON seasons
        # construct tags from list of season+year, increasing year for December
        ys = []
        for i in range(n_t):
            m = months[i]
            s = seasons[i]
            y = years[i]
            if m == '12':
                y = str(int(y) + 1)
            ys.append(y + s)
        l_tags = ys
    else:
        raise RuntimeError('freqency {:s} not implemented'.format(freq))

    # add tags to buffer DataArray
    buffer = da.copy()
    buffer.coords['tags'] = ('time', l_tags)

    # return groupby according to tags
    return buffer.groupby('tags')


def get_ev_length(ev, verbose=1, method=2):
    r"""Function computing event length

    :param ev: xarray DataArray
       multi dimensional array with time dimension and different values
       for different events
    verbose : int
      verbose flag, 1 makes the function verbose
    method : int
      two method of computing are in the code. Method 2 is faster by 50%
      but keeping method 1 in case.

    :return: xarray DataArray
       Array with lengths of each event sequence


    e.g

    with input = [0,0,1,1,1,0,0,1,1,1,1], output = [2,2,3,3,3,2,2,4,4,4,4]
         input = [0,1,1,2,2,0,0,0], output = [1,2,2,2,2,3,3,3]

    Has been tested with 1D and 3D DataArray

    # inspire/copy of :
    # https://stackoverflow.com/questions/45886518/identify-consecutive-same-values-in-pandas-dataframe-with-a-groupby
    """

    # make sure we have a time dimension
    assert ('time' in ev.dims)

    # create mask of event change, 1 if no change and 0 otherwise
    # fill first value with 1
    start = ev.isel(time=0)
    if ev.ndim == 1:
        # special 1d case
        start.values = 1
    else:
        start.values[:] = 1
    # compute difference and apply mask
    ev_diff = (ev.diff(dim='time') != 0) * 1
    # add start
    ev_diff = xr.concat((start, ev_diff), dim='time')

    # make cumulative sum
    diff_cumsum = ev_diff.cumsum(dim='time')

    # treatment depends on number fo dimensions
    if ev.ndim == 1:
        ev_l = ev.copy()
        v = diff_cumsum.values
        s = pd.Series(v)
        d = s.map(s.value_counts())
        ev_l.values[:] = d
        return ev_l
    else:

        # reshape in 2D to simplify loop
        non_time_dims = [d for d in diff_cumsum.dims if d != 'time']
        mcumsum = diff_cumsum.stack(z=non_time_dims)
        nz = mcumsum.sizes['z']
        time0 = time.time()

        # prepare output
        ev_l = mcumsum.copy()

        # loop and try different methods. Method 2 seems faster by 50%

        if verbose:
            print('get_ev_lenght method {:}'.format(method))
        if method == 1:
            for z in range(nz):
                v = mcumsum.isel(z=z).values
                s = pd.Series(v)
                d = s.map(s.value_counts())
                ev_l.isel(z=z).values[:] = d
                if verbose == 1:
                    if z % 500 == 0:
                        msg = 'in get_ev_lenght {:}/{:}'.format(z, nz)
                        print(msg)
        elif method == 2:
            for z in range(nz):
                v = mcumsum.isel(z=z).values
                u, ind = np.unique(v, return_index=True)
                i0 = 0
                d = np.zeros_like(v)
                for i in ind:
                    ll = i - i0
                    d[i0:i] = ll
                    i0 = i
                d[i:] = d.size - i
                ev_l.isel(z=z).values[:] = d
                if verbose == 1:
                    if z % 500 == 0:
                        msg = 'in get_ev_lenght {:}/{:}'.format(z, nz)
                        print(msg)

        if verbose:
            print('loop in get_ev_length done in {:10.2f}s'.format(time.time() - time0))

        # go back to original shape and return event length
        ev_l = ev_l.unstack('z')
        return ev_l


def get_ev_end(ev):
    r"""
    function flaging places when an event sequence ends

    :param ev: xarray DataArray
        array containing 1 for events and 0 for non-events
    :return: ev_end

    e.g. input = [0,0,1,1,1,0,0,1] returns [0,0,0,0,1,0,0,1]

    """

    # find when events finish and mask all other event points
    d = ev.diff(dim='time')
    ev_end = xr.where(d == -1, 1, 0)

    # shift end of events back for proper time alignment
    ev_end['time'] = ev.time[:-1]
    # deal with cases when last timestep is end of period
    ev_end = xr.concat((ev_end, ev.isel(time=-1)), 'time')
    return ev_end


def get_ev_start(ev):
    r"""
    function flaging places when an event sequence starts

    :param ev: xarray DataArray
        array containing 1 for events and 0 for non-events
    :return: ev_end

    e.g. input = [1,0,1,1,1,0,0,1] returns [1,0,1,0,0,0,0,1]

    """

    # find when events finish and mask all other event points
    d = ev.diff(dim='time')
    ev_start = xr.where(d == 1, 1, 0)

    # copy first timestep of ev to catch those start
    ev_start = xr.concat((ev.isel(time=0), ev_start), 'time')
    return ev_start


class Indicator(object):
    identifier = ''
    units = ''
    required_units = ''
    long_name = ''
    standard_name = ''
    description = ''
    keywords = ''

    def compute(self, *args, **kwds):
        """Index computation method. To be subclassed"""
        raise NotImplementedError

    def convert_units(self, *args):
        """Return DataArray with correct units, defined by `self.required_units`."""
        raise NotImplementedError

    def cfprobe(self, *args):
        """Check input data compliance to expectations.
        Warn of potential issues."""
        raise NotImplementedError

    def validate(self, *args):
        """Validate input data requirements.
        Raise error if conditions are not met."""
        raise NotImplementedError

    def decorate(self, da):
        """Modify output's attributes in place."""
        da.attrs.update(self.attrs)

    def missing(self, *args, **kwds):
        """Return boolean DataArray . To be subclassed"""
        raise NotImplementedError

    def __init__(self):
        # Extract DataArray arguments from compute signature.
        self.attrs = {'long_name': self.long_name,
                      'units': self.units,
                      'standard_name': self.standard_name
                      }

    def __call__(self, *args, **kwds):
        self.validate(*args)
        self.cfprobe(*args)

        cargs = self.convert_units(*args)

        out = self.compute(*cargs, **kwds)
        self.decorate(out)

        return out.where(self.missing(*cargs, freq=kwds['freq']))  # Won't work if keyword is passed as positional arg.
