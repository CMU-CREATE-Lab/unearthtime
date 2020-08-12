# UnearthTime

`UnearthTime` is a flexible automation framework for testing **EarthTime** using [`Selenium`](https://selenium-python.readthedocs.io/).

## Installation

Download `.whl` under Releases

```
pip install unearthtime-0.1.0a0-py3-none-any.whl
```

or

```
pip install git+https://github.com/CMU-CREATE-Lab/unearthtime.git#egg=unearthtime
```
 
## Examples

Using `geckodriver.exe` for `Firefox` on `Windows`.

```py
from selenium.webdriver import Firefox
from unearthtime.earthtime import EarthTime

## Printing full library of predefined locators

from unearthtime.explore.library import Library

for locator in Library
    print(locator)

## Searching Data Library

from unearthtime.tools.search import DLSearchEngine

with EarthTime.explore(driver=lambda: Firefox(executable_path='./geckodriver.exe')) as earthtime:
    dls = DLSearchEngine.informed(earthtime)
    us_race = dls.search('US Race')
    us_race_2014 = dls.search(' 2014', clear=False)

## Getting only the selected layers

from unearthtime.tools.layer import Layer

with EarthTime.explore(driver=lambda: Firefox(executable_path='./geckodriver.exe')) as earthtime:
    selected_checkboxes = list(map(lambda element: element.checked, earthtime.pull('DataLibraryCheckboxes', forced=True)))
    layers = [Layer.from_element(checkbox.parent_element(), earthtime) for checkbox in selected_checkboxes)]  
    
## Testing Draw Times of Layers in Data Library of 'https://earthtime.org/explore'

from unearthtime.tools.layer import Category

layer_times = {}

with EarthTime.explore(driver=lambda: Firefox(executable_path='./geckodriver.exe')) as earthtime:
    for name, category in Category.layers_by_category(earthtime):
        times = category.time_layers()
        layer_times[name] = {layer.title : layer.draw_time for layer in times if layer.draw_time > 0}

```
        
     
     
     
     
     
     
     
    
    
