# Adapted from https://github.com/tomkwok/calplot/blob/master/calplot/calplot.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime
from dateutil.relativedelta import relativedelta
from matplotlib.patches import Polygon
from matplotlib.colors import ColorConverter, ListedColormap

def plot_year_heatmap(data, year=None, how=None, dropzero=None, vmin=None, vmax=None,
                          ax=None, linecolor=None, cmap='viridis', fillcolor='lightgray',
                          linewidth=1, monthlabels=None, monthticks=True, monthlabeloffset=15,
                          daylabels=None, dayticks=True, textformat=None, textcolor='black',
                          textfiller='', edgecolor='black', **kwargs):
    
    if year is None:
        # Choose the financial year based on the first date in the index
        min_date = data.index.min()
        year = min_date.year if min_date.month >= 4 else min_date.year + 1

    # Resample if needed
    by_day = data if how is None else data.resample('D').agg(how)

    # Drop zeros if over 50% of values are zero, unless explicitly disabled
    if dropzero is not False:
        zero_ratio = (by_day == 0).sum() / by_day.count()
        if zero_ratio.any() > 0.5:
            dropzero = True

    if dropzero:
        by_day = by_day.replace(0, np.nan).dropna()

    vmin = by_day.min() if vmin is None else vmin
    vmax = by_day.max() if vmax is None else vmax
    ax = ax or plt.gca()

    # Determine line color fallback
    if linecolor is None:
        bg_color = ax.get_facecolor()
        linecolor = 'white' if ColorConverter().to_rgba(bg_color)[-1] == 0 else bg_color

    # Ensure all days are present
    start_date = pd.Timestamp(f'{year}-04-01')
    end_date = pd.Timestamp(f'{year + 1}-03-31')
    full_range = pd.date_range(start=start_date, end=end_date, freq='D', tz=data.index.tz)
    
    # Filter for the year
    try:
        by_day = data[start_date:end_date]
    except KeyError:
        pass  # May be empty due to dropzero
    
    by_day = by_day.reindex(full_range[:-1])
    
    start_week = by_day.index[0].isocalendar().week
    week_numbers = ((by_day.index - start_date).days // 7).astype(int)

    # Prepare plotting data
    by_day = pd.DataFrame({
        'data': by_day,
        'fill': 1,
        'day': by_day.index.dayofweek,
        'week': week_numbers
    })

    # Normalize weeks for edge cases (week 0 or 53 issues)
    by_day.loc[(by_day.index.month == 1) & (by_day.week > 50), 'week'] = 0
    by_day.loc[(by_day.index.month == 12) & (by_day.week < 10), 'week'] = by_day.week.max() + 1

    # Create pivoted heatmap arrays
    plot_data = by_day.pivot(index='day', columns='week', values='data').values[::-1]
    plot_data = np.ma.masked_invalid(plot_data)

    fill_data = by_day.pivot(index='day', columns='week', values='fill').values[::-1]
    fill_data = np.ma.masked_invalid(fill_data)

    # Plot background and actual data
    ax.pcolormesh(fill_data, vmin=0, vmax=1, cmap=ListedColormap([fillcolor]))
    ax.pcolormesh(plot_data, vmin=vmin, vmax=vmax, cmap=cmap,
                  linewidth=linewidth, edgecolors=linecolor, **kwargs)

    # Formatting
    ax.set(xlim=(0, plot_data.shape[1]), ylim=(0, plot_data.shape[0]), aspect='equal')
    ax.spines[:].set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)

    # Month and day labels
    if monthlabels is None:
        monthlabels = ['Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep',
                   'Oct', 'Nov', 'Dec', 'Jan', 'Feb', 'Mar']
    if daylabels is None:
        daylabels = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']

    # X-axis month ticks
    if monthticks is True:
        monthticks = range(len(monthlabels))
    elif not monthticks:
        monthticks = []

    xtick_pos = []
    for i in monthticks:
        month = (i + 4 - 1) % 12 + 1  # April = 4, wraps around after December
        dt = datetime.date(year if month >= 4 else year + 1, month, monthlabeloffset)
        if pd.Timestamp(dt) in by_day.index:
            xtick_pos.append(by_day.loc[pd.Timestamp(dt), 'week'])
    ax.set_xticks(xtick_pos)
    ax.set_xticklabels([monthlabels[i] for i in monthticks])
    ax.set_xlabel('')

    # Y-axis day ticks
    if dayticks is True:
        dayticks = range(len(daylabels))
    elif not dayticks:
        dayticks = []

    ax.set_yticks([6 - i + 0.5 for i in dayticks])
    ax.set_yticklabels([daylabels[i] for i in dayticks], rotation='horizontal', va='center')
    ax.yaxis.set_ticks_position('right')
    ax.set_ylabel('')

    # Optional text annotations
    if textformat is not None:
        for y in range(plot_data.shape[0]):
            for x in range(plot_data.shape[1]):
                val = plot_data[y, x]
                content = textfiller if val is np.ma.masked and fill_data[y, x] == 1 else (
                    textformat.format(val) if not np.ma.is_masked(val) else '')
                ax.text(x + 0.5, y + 0.5, content, color=textcolor, ha='center', va='center')

    # Month border outlines
    start_weekday = start_date.weekday()
    for i in range(12):
        month = (i + 4 - 1) % 12 + 1
        year_offset = year if month >= 4 else year + 1

        first = datetime.date(year_offset, month, 1)
        last = (pd.Timestamp(first) + pd.offsets.MonthEnd(0)).date()

        y0 = 7 - first.weekday()
        y1 = 7 - last.weekday()
        x0 = (pd.Timestamp(first) - start_date).days // 7
        x1 = (pd.Timestamp(last) - start_date).days // 7

        P = [(x0, y0), (x0+1, y0), (x0+1, 7), (x1+1, 7),
             (x1+1, y1-1), (x1, y1-1), (x1, 0), (x0, 0)]
        ax.add_artist(Polygon(P, edgecolor=edgecolor, facecolor='None',
                              linewidth=linewidth, zorder=20, clip_on=False))
    return ax

def yearmonthdayplot(data, how='sum',
            yearlabels=True, yearascending=True,
            yearlabel_kws=None, subplot_kws=None, gridspec_kws=None,
            figsize=None, fig_kws=None, colorbar=None,
            suptitle=None, suptitle_kws=None,
            tight_layout=True, **kwargs):
    
    if yearlabel_kws is None:
        yearlabel_kws = dict()
    if subplot_kws is None:
        subplot_kws = dict()
    if gridspec_kws is None:
        gridspec_kws = dict()
    if fig_kws is None:
        fig_kws = dict()
    if suptitle_kws is None:
        suptitle_kws = dict()

    years = np.unique(data.index.year)[:-1]
    if not yearascending:
        years = years[::-1]

    if colorbar is None:
        colorbar = data.nunique() > 1

    if figsize is None:
        figsize = (10+(colorbar*2), 2*len(years))

    fig, axes = plt.subplots(nrows=len(years), ncols=1, squeeze=False,
                             figsize=figsize,
                             subplot_kw=subplot_kws,
                             gridspec_kw=gridspec_kws, **fig_kws)
    axes = axes.T[0]

    # We explicitely resample by day only once. This is an optimization.
    by_day = data
    if how is not None:
        by_day = by_day.resample('D').agg(how)        
        
    data_min = by_day.min().min()
    data_max = by_day.max().max()
    abs_max = max(abs(data_min), abs(data_max))
    abs_min = min(abs(data_min), abs(data_max))
    vmin = -abs_min
    vmax = 200

    ylabel_kws = dict(
        fontsize=16,
        color='gray',
        fontfamily='Sans Serif',
        fontweight='bold',
        ha='center')
    ylabel_kws.update(yearlabel_kws)

    max_weeks = 0

    for year, ax in zip(years, axes):
        plot_year_heatmap(by_day, year=year, how=None, ax=ax, vmin=vmin, vmax=vmax, **kwargs)
        max_weeks = max(max_weeks, ax.get_xlim()[1])

        if yearlabels:
            ax.set_ylabel(str(year)+'-'+str(year+1), **ylabel_kws)

    # In a leap year it might happen that we have 54 weeks (e.g., 2020).
    # Here we make sure the width is consistent over all years.
    for ax in axes:
        ax.set_xlim(0, max_weeks)

    stitle_kws = dict()

    if tight_layout:
        plt.tight_layout()
        stitle_kws.update({'y': 1})

    if colorbar:
        if tight_layout:
            stitle_kws.update({'x': 0.425, 'y': 1.03})

        if len(years) == 1:
            fig.colorbar(axes[0].get_children()[1], ax=axes.ravel().tolist(),
                         orientation='vertical')
        else:
            fig.subplots_adjust(right=0.8)
            cax = fig.add_axes([0.85, 0.025, 0.02, 0.95])
            fig.colorbar(axes[0].get_children()[1], cax=cax, orientation='vertical')

    stitle_kws.update(suptitle_kws)
    plt.suptitle(suptitle,fontweight='bold', **stitle_kws)

    return fig, axes
