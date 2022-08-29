# noqa: D205,D400
r"""
=============================================
McArthur Forest Fire Danger Indices Submodule
=============================================

This submodule defines the :py:func:`xclim.indices.keetch_byram_drought_index`,
:py:func:`xclim.indices.griffiths_drought_factor` and :py:func:`xclim.indices.mcarthur_forest_fire_danger_index`
indices, which are used by the eponym indicators. Users should read this module's documentation and consult
:cite:t:`ffdi-finkele_2006` which provides details of the methods used to calculate each index.
"""
# This file is structured in the following way:
# Section 1: individual codes, numba-accelerated and vectorized functions.
# Section 2: Exposed methods and indices.
#
# Methods starting with a "_" are not usable with xarray objects, whereas the others are.
from __future__ import annotations

import numpy as np
import xarray as xr
from numba import float64, guvectorize, int64

from xclim.core.units import convert_units_to, declare_units

__all__ = [
    "griffiths_drought_factor",
    "keetch_byram_drought_index",
    "mcarthur_forest_fire_danger_index",
]

# SECTION 1 - Codes - Numba accelerated and vectorized functions


@guvectorize(
    [
        (
            float64[:],
            float64[:],
            float64,
            float64,
            float64[:],
        )
    ],
    "(n),(n),(),()->(n)",
)
def _keetch_byram_drought_index(p, t, pa, kbdi0, kbdi: float):  # pragma: no cover
    """Compute the Keetch-Byram drought (KBDI) index.

    Parameters
    ----------
    p : array_like
        Total rainfall over previous 24 hours [mm].
    t : array_like
        Maximum temperature near the surface over previous 24 hours [C].
    pa : float
        Mean annual accumulated rainfall.
    kbdi0 : float
        Previous value of the Keetch-Byram drought index used to initialise the KBDI calculation.

    Returns
    -------
    array_like
        Keetch-Byram drought index.
    """
    rr = 5.0

    for d in range(len(p)):
        # Reset remaining runoff if there is zero rainfall
        if p[d] == 0.0:
            rr = 5.0

        # Calculate the runoff for this timestep
        if p[d] < rr:
            r = p[d]
        else:
            r = rr

        Peff = p[d] - r
        ET = (
            1e-3
            * (203.2 - kbdi0)
            * (0.968 * np.exp(0.0875 * t[d] + 1.5552) - 8.3)
            / (1 + 10.88 * np.exp(-0.00173 * pa))
        )
        kbdi0 = kbdi0 - Peff + ET

        # Limit kbdi to between 0 and 200 mm
        if kbdi0 < 0.0:
            kbdi0 = 0.0

        if kbdi0 > 203.2:
            kbdi0 = 203.2

        rr = rr - r
        kbdi[d] = kbdi0


@guvectorize(
    [
        (
            float64[:],
            float64[:],
            int64,
            float64[:],
        )
    ],
    "(n),(n),()->(n)",
)
def _griffiths_drought_factor(p, smd, lim, df):  # pragma: no cover
    """Compute the Griffiths drought factor.

    Parameters
    ----------
    p : array_like
        Total rainfall over previous 24 hours [mm].
    smd : array_like
        Soil moisture deficit (e.g. KBDI).
    lim : integer
        How to limit the drought factor.
        If 0, use equation (14) in :cite:t:`ffdi-finkele_2006`.
        If 1, use equation (13) in :cite:t:`ffdi-finkele_2006`.

    Returns
    -------
    df : array_like
        The limited Griffiths drought factor
    """
    wl = 20  # 20-day window length

    for d in range(wl - 1, len(p)):
        pw = p[d - wl + 1 : d + 1]

        # Calculate the x-function from significant rainfall
        # events
        conseq = 0
        pmax = 0.0
        P = 0.0
        x = 1.0
        for iw in range(wl):
            event = pw[iw] > 2.0
            event_end = ~event & (conseq != 0)
            final_event = event & (iw == (wl - 1))

            if event:
                conseq = conseq + 1
                P = P + pw[iw]
                if pw[iw] >= pmax:
                    N = wl - iw
                    pmax = pw[iw]

            if event_end | final_event:
                # N = 0 defines a rainfall event since 9am today,
                # so doesn't apply here, where p is the rainfall
                # over previous 24 hours.
                x_ = N**1.3 / (N**1.3 + P - 2.0)
                x = min(x_, x)

                conseq = 0
                P = 0.0
                pmax = 0.0

        if lim == 0:
            if smd[d] < 20:
                xlim = 1 / (1 + 0.1135 * smd[d])
            else:
                xlim = 75 / (270.525 - 1.267 * smd[d])
            if x > xlim:
                x = xlim

        dfw = (
            10.5
            * (1 - np.exp(-(smd[d] + 30) / 40))
            * (41 * x**2 + x)
            / (40 * x**2 + x + 1)
        )

        if lim == 1:
            if smd[d] < 25.0:
                dflim = 6.0
            elif (smd[d] >= 25.0) & (smd[d] < 42.0):
                dflim = 7.0
            elif (smd[d] >= 42.0) & (smd[d] < 65.0):
                dflim = 8.0
            elif (smd[d] >= 65.0) & (smd[d] < 100.0):
                dflim = 9.0
            else:
                dflim = 10.0
            if dfw > dflim:
                dfw = dflim

        if dfw > 10.0:
            dfw = 10.0

        df[d] = dfw


# SECTION 2 - Public methods and indices


def _keetch_byram_drought_index_pass(pr, tasmax, pr_annual, kbdi0):
    """Pass inputs on to guvectorized function `_keetch_byram_drought_index`. DO NOT CALL DIRECTLY, use `keetch_byram_drought_index` instead."""
    # This function is actually only required as xr.apply_ufunc will not receive
    # a guvectorized function which has the output(s) in its function signature
    return _keetch_byram_drought_index(pr, tasmax, pr_annual, kbdi0)


# @declare_units(
#     pr="[precipitation]",
#     tasmax="[temperature]",
#     pr_annual="[precipitation]",
#     kbdi0="[]",
# )
def keetch_byram_drought_index(
    pr: xr.DataArray,
    tasmax: xr.DataArray,
    pr_annual: xr.DataArray,
    kbdi0: xr.DataArray | None = None,
) -> xr.DataArray:
    """Calculate the Keetch-Byram drought index (KBDI).

    This method implements the methodology and formula described in :cite:t:`ffdi-finkele_2006`
    (section 2.1.1) for calculating the KBDI. See Notes below.

    Parameters
    ----------
    pr : xr.DataArray
        Total rainfall over previous 24 hours [mm/day].
    tasmax : xr.DataArray
        Maximum temperature near the surface over previous 24 hours [degC].
    pr_annual: xr.DataArray
        Mean (over years) annual accumulated rainfall [mm/year].
    kbdi0 : xr.DataArray, optional
        Previous KBDI map used to initialise the KBDI calculation [mm/day]. Defaults to 0.

    Returns
    -------
    kbdi : xr.DataArray
        Keetch-Byram drought index.

    Notes
    -----
    :cite:t:`ffdi-finkele_2006` limits the maximum KBDI to 200 mm to represent the maximum field capacity of the soil
    (8 in according to :cite:t:`ffdi-keetch_1968`). However, it is more common in the literature to limit the KBDI to
    203.2 mm which is a more accurate conversion from in to mm. In the function, the KBDI is limited to 203.2 mm.

    References
    ----------
    :cite:cts:`ffdi-keetch_1968,ffdi-finkele_2006,ffdi-holgate_2017,ffdi-dolling_2005`
    """
    pr = convert_units_to(pr, "mm/day")
    tasmax = convert_units_to(tasmax, "C")
    pr_annual = convert_units_to(pr_annual, "mm/year")
    if kbdi0 is not None:
        kbdi0 = convert_units_to(kbdi0, "mm/day")

    if kbdi0 is None:
        kbdi0 = xr.full_like(pr.isel(time=0), 0)

    return xr.apply_ufunc(
        _keetch_byram_drought_index_pass,
        pr,
        tasmax,
        pr_annual,
        kbdi0,
        input_core_dims=[["time"], ["time"], [], []],
        output_core_dims=[["time"]],
        dask="parallelized",
        output_dtypes=[pr.dtype],
    )


def _griffiths_drought_factor_pass(pr, smd, lim):
    """Pass inputs on to guvectorized function `_griffiths_drought_factor`. DO NOT CALL DIRECTLY, use `griffiths_drought_factor` instead."""
    # This function is actually only required as xr.apply_ufunc will not receive
    # a guvectorized function which has the output(s) in its function signature
    return _griffiths_drought_factor(pr, smd, lim)


# @declare_units(
#     pr="[precipitation]",
#     smd="[precipitation]",
# )
def griffiths_drought_factor(
    pr: xr.DataArray,
    smd: xr.DataArray,
    limiting_func: str = "xlim",
) -> xr.DataArray:
    """Calculate the Griffiths drought factor based on the soil moisture deficit.

    This method implements the methodology and formula described in :cite:t:`ffdi-finkele_2006`
    (section 2.2) for calculating the Griffiths drought factor.

    Parameters
    ----------
    pr : xr.DataArray
      Total rainfall over previous 24 hours [mm/day].
    smd : xarray DataArray
      Daily soil moisture deficit (often KBDI) [mm/day].
    limiting_func : {"xlim", "discrete"}
      How to limit the values of the drought factor.
      If "xlim" (default), use equation (14) in :cite:t:`ffdi-finkele_2006`.
      If "discrete", use equation Eq (13) in :cite:t:`ffdi-finkele_2006`.

    Returns
    -------
    df : xr.DataArray
      The limited Griffiths drought factor.

    Notes
    -----
    Calculation of the Griffiths drought factor depends on the rainfall over the previous 20 days.
    Thus, the first available time point in the drought factor returned by this function
    corresponds to the 20th day of the input data.

    References
    ----------
    :cite:cts:`ffdi-griffiths_1999,ffdi-finkele_2006,ffdi-holgate_2017`
    """
    pr = convert_units_to(pr, "mm/day")
    smd = convert_units_to(smd, "mm/day")

    if limiting_func == "xlim":
        lim = 0
    elif limiting_func == "discrete":
        lim = 1
    else:
        raise ValueError(f"{limiting_func} is not a valid input for `limiting_func`")

    df = xr.apply_ufunc(
        _griffiths_drought_factor_pass,
        pr,
        smd,
        kwargs=dict(lim=lim),
        input_core_dims=[["time"], ["time"]],
        output_core_dims=[["time"]],
        dask="parallelized",
        output_dtypes=[pr.dtype],
    )

    # First non-zero entry is at the 19th time point since df is calculated
    # from a 20-day rolling window
    return df.isel(time=slice(19, None))


# @declare_units(
#     D="[]",
#     T="[temperature]",
#     H="[]",
#     V="[speed]",
# )
def mcarthur_forest_fire_danger_index(
    D: xr.DataArray,
    T: xr.DataArray,
    H: xr.DataArray,
    V: xr.DataArray,
):
    """Calculate the McArthur forest fire danger index (FFDI) Mark 5.

    This method calculates the FFDI using the formula in :cite:t:`ffdi-noble_1980`.

    Parameters
    ----------
    D : xr.DataArray
        The drought factor to use in the FFDI calculation. Often the daily Griffiths
        drought factor (see `griffiths_drought_factor`).
    T : xr.DataArray
        The temperature to use in the FFDI calculation [degC]. Often the current or previous
        day's maximum daily temperature near the surface.
    H : xr.DataArray
        The relative humidity to use in the FFDI calculation [%]. Often the relative humidity
        near the time of the maximum temperature used for T.
    V : xr.DataArray
        The wind speed to use in the FFDI calculation [km/h]. Often mid-afternoon wind speed at
        a height of 10m.

    Returns
    -------
    ffdi : xr.DataArray
        The McArthur forest fire danger index.

    References
    ----------
    :cite:cts:`ffdi-noble_1980,ffdi-dowdy_2018,ffdi-holgate_2017`
    """
    T = convert_units_to(T, "C")
    H = convert_units_to(H, "pct")
    V = convert_units_to(V, "km/h")

    return D**0.987 * np.exp(0.0338 * T - 0.0345 * H + 0.0234 * V + 0.243147)
