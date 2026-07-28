"""The paper's only figure, generated as SVG by hand.

Written as plain text rather than with a plotting library for the same reason
everything else here is standard library: a figure produced by a dependency is a
figure nobody can regenerate in ten years.

The output is a pure function of the observed counts, with fixed number
formatting, so it is byte-for-byte reproducible. `checks/check_60_figure.py`
regenerates it in memory and compares it against the committed file. A figure
that no longer matches the data is a failed build, not a stale image.
"""

WIDTH = 640
HEIGHT = 360
MARGIN_LEFT = 56
MARGIN_RIGHT = 16
MARGIN_TOP = 28
MARGIN_BOTTOM = 48

#: Top of the value axis. Fixed rather than derived from the data so that the
#: figure's vertical scale does not silently change when the data change.
Y_MAX = 130
Y_TICK_STEP = 26


def _plot_area():
    left = MARGIN_LEFT
    right = WIDTH - MARGIN_RIGHT
    top = MARGIN_TOP
    bottom = HEIGHT - MARGIN_BOTTOM
    return left, right, top, bottom


def render_svg(counts, expected):
    """Return the figure for `counts` with the null expectation drawn at `expected`."""
    left, right, top, bottom = _plot_area()
    plot_width = right - left
    plot_height = bottom - top
    slot = plot_width / float(len(counts))
    bar_width = slot * 0.62

    def y_of(value):
        return bottom - plot_height * (float(value) / Y_MAX)

    lines = []
    add = lines.append
    add('<?xml version="1.0" encoding="UTF-8"?>')
    add('<svg xmlns="http://www.w3.org/2000/svg" width="%d" height="%d" '
        'viewBox="0 0 %d %d" font-family="Helvetica, Arial, sans-serif">'
        % (WIDTH, HEIGHT, WIDTH, HEIGHT))
    add('<rect width="%d" height="%d" fill="#ffffff"/>' % (WIDTH, HEIGHT))

    # Value axis with ticks and gridlines.
    tick = 0
    while tick <= Y_MAX:
        y = y_of(tick)
        add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#e3e3e3" stroke-width="1"/>'
            % (left, y, right, y))
        add('<text x="%.2f" y="%.2f" font-size="11" fill="#555555" text-anchor="end">%d</text>'
            % (left - 8, y + 4, tick))
        tick += Y_TICK_STEP

    # Bars.
    for index, count in enumerate(counts):
        x = left + index * slot + (slot - bar_width) / 2.0
        y = y_of(count)
        add('<rect x="%.2f" y="%.2f" width="%.2f" height="%.2f" fill="#4a6f8a"/>'
            % (x, y, bar_width, bottom - y))
        add('<text x="%.2f" y="%.2f" font-size="11" fill="#333333" text-anchor="middle">%d</text>'
            % (x + bar_width / 2.0, y - 5, count))
        add('<text x="%.2f" y="%.2f" font-size="12" fill="#333333" text-anchor="middle">%d</text>'
            % (x + bar_width / 2.0, bottom + 18, index))

    # The null expectation.
    y_expected = y_of(expected)
    add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#b03a2e" '
        'stroke-width="1.5" stroke-dasharray="6 4"/>' % (left, y_expected, right, y_expected))
    add('<text x="%.2f" y="%.2f" font-size="11" fill="#b03a2e" text-anchor="end">'
        'expected %d</text>' % (right, y_expected - 6, expected))

    # Axis line and labels.
    add('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="#333333" stroke-width="1"/>'
        % (left, bottom, right, bottom))
    add('<text x="%.2f" y="%.2f" font-size="12" fill="#333333" text-anchor="middle">'
        'decimal digit</text>' % ((left + right) / 2.0, HEIGHT - 12))
    add('<text x="14" y="%.2f" font-size="12" fill="#333333" text-anchor="middle" '
        'transform="rotate(-90 14 %.2f)">observed count</text>'
        % ((top + bottom) / 2.0, (top + bottom) / 2.0))
    add('</svg>')
    return "\n".join(lines) + "\n"
