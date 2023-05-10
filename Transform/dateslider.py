# Import Dependencies

import pandas as pd
import numpy as np

from datetime import datetime
from bokeh.models import ColumnDataSource, HoverTool, DateSlider
from bokeh.plotting import figure
from bokeh.io import curdoc, show
from bokeh.tile_providers import get_provider, OSM
from bokeh.layouts import row, column

df = pd.read_csv("district_crime_df.csv")
df['occurrenceyear'] = df['occurrenceyear'].astype(str)

radius_scale = 100

# Mercator units conversion
def wgs84_to_web_mercator(df, lon, lat):
    """Converts decimal longitude/latitude to Web Mercator format"""
    k = 6378137
    df["x"] = df[lon] * (k * np.pi/180.0)
    df["y"] = np.log(np.tan((90 + df[lat]) * np.pi/360.0)) * k
    return df
df = wgs84_to_web_mercator(df, 'd_lon', 'd_lat')

source = ColumnDataSource(df)

# Map zoom scale
scale = 2500
x = df['x']
y = df['y']

# Centers map
x_min = int(x.mean() - (scale * 1))
x_max = int(x.mean() + (scale * 1))
y_min = int(y.mean() - (scale * 10))
y_max = int(y.mean() + (scale * 10))

# Prepare Bokeh
plot = figure(
    title = 'Toronto District Crime Rate',
    match_aspect = True,
    tools = 'wheel_zoom, pan, reset, save',
    x_range = (x_min, x_max), y_range = (y_min, y_max),
    x_axis_type = 'mercator', y_axis_type = 'mercator',
    width = 900
    )
plot.grid.visible = True
# Get map
map = plot.add_tile(get_provider(OSM))
map.level = 'underlay'

plot.xaxis.visible = False
plot.yaxis.visible = False
plot.title.text_font_size = "20px"

def bubble_map(plot, df_source, radius_col_plot, radius_col, state, color='orange', leg_label='Bubble Map'):
    source = df_source
    c = plot.circle(x = 'x', y = 'y', color = color, source = source, size = 1, fill_alpha = 0.1, radius = radius_col_plot,\
                    legend_label = leg_label, hover_color = 'red')

    tip_label = '@' + radius_col
    state_label = '@' + state

    circle_hover = HoverTool(tooltips = [("Percentage " + leg_label, tip_label + "%"), ('State', state_label)], mode = 'mouse',\
                             point_policy = 'follow_mouse', renderers = [c])
    circle_hover.renderers.append(c)
    
    plot.tools.append(circle_hover)
    plot.legend.location = "top_right"
    plot.legend.click_policy = "hide"

bubble_map(plot = plot,
           df_source = source, radius_col_plot = 'Crime_Per_1000', radius_col = 'Crime_Per_1000', leg_label = 'Crime_Per_1000',
           state = 'District', color = 'blue')

# ['d_lon', 'd_lat', 'District', 'occurrenceyear', 'Population','Total_Crimes', 'Crime_Per_1000']

date_slider = DateSlider(start = min(df.date), end = max(df.date), value = min(df.date), step = int(86400000*366), title = "Year")

def update_plot(attr, old, new):
    datesel = datetime.fromtimestamp(new / 1000).strftime('%Y')
    print(datesel, new)
    new_data = df[df['occurrenceyear'] == datesel]
    source.data.update(ColumnDataSource(new_data).data)

date_slider.on_change('value', update_plot)

curdoc().add_root(column(date_slider, plot))

# layout = column(plot, date_slider)

# show(layout)