# UnearthTime

`UnearthTime` is a flexible automation framework for testing **EarthTime** using [`Selenium`](https://selenium-python.readthedocs.io/).

Requires:
  * Selenium
  * OpenCV
  * scikit-image
  * NumPy
 
## Example: Testing Draw Times of Layers in Data Library

Note: 

This example tests over 3000 layers and crashes Chrome. A way around this is to
 * Test categories in groups using several Chrome windows
    * The method `Category.layers_by_category_after('category_id', environment)` in `mechanic.layer.Category` will help with this. Note, this method gathers layers from categories **after** the input one.
    
 * Test using Firefox


```py
from environment import Environment
from mechanic.layer import Category
from timeit import default_timer as timer
from selenium.webdriver import Firefox

import time

draw_times = {}

# Default URL for Environment is 'https://earthtime.org/explore'
# To change this, either input the URL as the first argument,
#  or specify it by keyword

with Environment.explore(driver=lambda: Firefox(executable_path='drivers/geckodriver.exe')) as env:
 
    for name, category in Category.layers_by_category_of(env).items():
        layer_times = {}
        category.inform()
      
        for layer in category:
   
            # Skip blank layers
            if layer.title:
                draw_calls = 0
                start = timer()
                layer.select()
                drawn = env.lastFrameCompletelyDrawn
    
                while not drawn:
                    draw_calls += 1
     
                    # Allowing at least 15s for each layer
                    if not env.isSpinnerShowing() and cycles >= 60:
                        break
                    else:
                        time.sleep(0.25)
                        drawn = env.lastFrameCompletelyDrawn
                    
                end = timer()
            
                layer.select()
            
                ttime = end - start
            
                layer_times[layer.title] = (ttime, draw_calls, drawn)
                
        draw_times[name] = layer_times
```

Other examples can be found in the [Reference](https://github.com/CMU-CREATE-Lab/unearthtime/blob/master/unearthtime/docs/Reference.md) doc, which is still under development.
        
     
     
     
     
     
     
     
    
    
