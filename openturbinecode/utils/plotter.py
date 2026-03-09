"""This module abstracts the plotting functions for the OpenTurbineCoDe project.
"""
import numpy as np
import matplotlib.pyplot as plt


def xy(data: np.ndarray, title: str, ylabel: str, xlabel: str, filename=None, show=True):
    """Create a simple xy plot.

    Args:
        data (np.ndarray): Numpy array with the data to plot.
        title (str): Plot title.
        ylabel (str): Plot y-axis label.
        xlabel (str): Plot x-axis label.
        filename (Path, optional): Path to file. Defaults to None.
        show (bool, optional): Show the plot. Defaults to True.
    """
    x_data = data[:, 0]
    y_data = data[:, 1]
    fig, ax = plt.subplots()
    ax.plot(x_data, y_data)
    ax.set(xlabel=xlabel, ylabel=ylabel, title=title)
    ax.grid()
    fig.savefig(filename) if filename else None
    plt.show() if show else None


def time_series(data: np.ndarray, title: str, ylabel: str, filename=None, show=False):
    xlabel = "Time [s]"
    xy(data, title, ylabel, xlabel, filename, show)
