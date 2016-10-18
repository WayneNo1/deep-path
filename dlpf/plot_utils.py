import pandas, itertools

import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt

LINES = '- -- -. : . , 0 v ^ < > 1 2 3 4 s p * h H + x D d | - _'.split(' ')
MARKERS = '. , o v ^ < > 1 2 3 4 8 s p * h H + x D d | _'.split(' ')
# STYLES_GEN = itertools.cycle([''.join(s) for s in itertools.product(LINES, MARKERS)])
STYLES_GEN = itertools.cycle(['-'])


def basic_plot(title_data_tuples, out_file = None):
    fig, ax = plt.subplots()
    fig.set_size_inches((20, 10))
    for (name, x, y), style in itertools.izip(title_data_tuples,
                                              STYLES_GEN):
        ax.plot(x, y, style, label = name)
    ax.legend()
    if not out_file is None:
        fig.savefig(out_file)
    return fig, ax


def basic_plot_from_df(df, out_file = None, need_get_dummies = True):
    if need_get_dummies and df.shape[1] > 0:
        df = pandas.get_dummies(df)
    return basic_plot(((col, df.index, df[col].values) for col in df.columns),
                      out_file = out_file)


def basic_plot_from_df_rolling_mean(df, window = None, smooth_factor = 50.0, out_file = None):
    if df.shape[1] > 0:
        df = pandas.get_dummies(df)
    if window is None:
        window = max(int(float(df.shape[0]) / smooth_factor), 10)
    df = pandas.rolling_mean(df, window)
    return basic_plot_from_df(df,
                              out_file = out_file,
                              need_get_dummies = False)


def basic_plot_via_df(raw_data, out_file = None):
    basic_plot_from_df(pandas.DataFrame(raw_data),
                       out_file = out_file)
