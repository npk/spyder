# -*- coding: utf-8 -*-
# -----------------------------------------------------------------------------
# Copyright © Spyder Project Contributors
#
# Licensed under the terms of the MIT License
# (see spyder/__init__.py for details)
# -----------------------------------------------------------------------------

"""
Tests for the widgets used in the Plots plugin.
"""

# Standard library imports
import os.path as osp
try:
    from unittest.mock import Mock
except ImportError:
    from mock import Mock  # Python 2

# Third party imports
import pytest
import matplotlib.pyplot as plt
import numpy as np

# Local imports
from spyder.plugins.plots.widgets.figurebrowser import FigureBrowser
from spyder.py3compat import to_text_string


# =============================================================================
# ---- Fixtures
# =============================================================================
@pytest.fixture
def figbrowser(qtbot):
    """An empty figure browser widget fixture."""
    figbrowser = FigureBrowser()
    figbrowser.set_shellwidget(Mock())
    figbrowser.setup(mute_inline_plotting=True, show_plot_outline=False)
    qtbot.addWidget(figbrowser)
    figbrowser.show()
    figbrowser.setMinimumSize(700, 500)
    return figbrowser


# =============================================================================
# ---- Helper functions
# =============================================================================
def create_figure(figname):
    """Create a matplotlib figure, save it to disk and return its data."""
    # Create and save to disk a figure with matplotlib.
    fig, ax = plt.subplots()
    fig.set_size_inches(6, 4)
    ax.plot(np.random.rand(10), '.', color='red')
    fig.savefig(figname)

    # Read back and return the binary data from the file.
    with open(figname, "rb") as img:
        fig = img.read()
    return fig


def add_figures_to_browser(figbrowser, nfig, tmpdir):
    """
    Create and add bitmap figures to the figure browser. Also return a list
    of the created figures data.
    """
    figs = []
    for i in range(nfig):
        figname = osp.join(to_text_string(tmpdir), 'mplfig' + str(i) + '.png')
        figs.append(create_figure(figname))
        figbrowser._handle_new_figure(figs[-1], 'image/png')

    assert len(figbrowser.thumbnails_sb._thumbnails) == nfig
    assert figbrowser.thumbnails_sb.current_thumbnail.canvas.fig == figs[-1]
    assert figbrowser.figviewer.figcanvas.fig == figs[-1]

    return figs


# =============================================================================
# ---- Tests
# =============================================================================
@pytest.mark.parametrize("fmt, fext",
                         [('image/png', '.png'), ('image/svg+xml', '.svg')])
def test_handle_new_figures(figbrowser, tmpdir, fmt, fext):
    """
    Test that the figure browser widget display correctly new figures in
    its viewer and thumbnails scrollbar.
    """
    assert len(figbrowser.thumbnails_sb._thumbnails) == 0
    assert figbrowser.thumbnails_sb.current_thumbnail is None
    assert figbrowser.figviewer.figcanvas.fig is None

    for i in range(3):
        figname = osp.join(to_text_string(tmpdir), 'mplfig' + str(i) + fext)
        fig = create_figure(figname)
        figbrowser._handle_new_figure(fig, fmt)
        assert len(figbrowser.thumbnails_sb._thumbnails) == i + 1
        assert figbrowser.thumbnails_sb.current_thumbnail.canvas.fig == fig
        assert figbrowser.figviewer.figcanvas.fig == fig


@pytest.mark.parametrize("fmt, fext",
                         [('image/png', '.png'), ('image/svg+xml', '.svg')])
def test_save_figure_to_file(figbrowser, tmpdir, mocker, fmt, fext):
    """
    Test saving png and svg figures to file with the figure browser.
    """
    # Create a figure with matplotlib and load it in the figure browser.
    mpl_figname = osp.join(to_text_string(tmpdir), 'mplfig' + fext)
    mplfig = create_figure(mpl_figname)
    figbrowser._handle_new_figure(mplfig, fmt)

    # Save the figure back to disk with the figure browser.
    spy_figname = osp.join(to_text_string(tmpdir), 'spyfig' + fext)
    mocker.patch('spyder.plugins.plots.widgets.figurebrowser.getsavefilename',
                 return_value=(spy_figname, fext))
    figbrowser.thumbnails_sb.save_current_figure_as()
    assert osp.exists(spy_figname)

    # Compare the figure created with matplotlib with the one created with our
    # figure browser.
    with open(spy_figname, "rb") as figfile:
        spyfig = figfile.read()
    assert mplfig == spyfig


if __name__ == "__main__":
    import os
    pytest.main([os.path.basename(__file__), '-vv', '-rw'])
