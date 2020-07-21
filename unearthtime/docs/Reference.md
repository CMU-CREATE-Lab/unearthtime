# 1. Unearthtime Reference Guide

## 1.1. Table of Contents

- [1. Unearthtime Reference Guide](#1-unearthtime-reference-guide)
  - [1.1. Table of Contents](#11-table-of-contents)
- [2. `Miss`](#2-miss)
- [3. `Hit`](#3-hit)
  - [3.1. Properties](#31-properties)
  - [3.2. Methods](#32-methods)
- [4. `Timelapse`](#4-timelapse)
  - [4.1. Examples](#41-examples)
  - [4.2. Methods](#42-methods)
- [5. `Environment`](#5-environment)
  - [5.1. Examples](#51-examples)
    - [5.1.1. Instantiation](#511-instantiation)
    - [5.1.2. Element access](#512-element-access)
    - [5.1.3. Page Interaction](#513-page-interaction)
  - [5.2. Properties](#52-properties)
  - [5.3. Methods](#53-methods)

<br>
<br>

# 2. `Miss`

Represents an always `False` missed request to the DOM

<br>
<br>

# 3. `Hit`

Represents a successful response to the DOM

<br>

---

## 3.1. Properties

---

**`selenium_id`** :&#8658; `str`
> The **Selenium** specific id

**`session`** :&#8658; `str`
> The **Selenium** specific session id

<br>

---

## 3.2. Methods

---

**`__init__(element)`**

> Parameters:
> * `element`: `WebElement`
> 	* The **Selenium** `WebElement` to be wrapped

---

**`__getattr__(attr)`** :&#8658; `str`

> Gets an attribute of the element, looking first at the tag attributes and then javascript attributes of the element

> Parameters:
> * `attr`: `str`
> 	* The name of the attribute

> Raises:
> * `AttributeError`
> 	* If this element doesn't have the attribute

> Notes:
> * *id* and *class* are special cases and can be accessed as `id_` and `class_` respectively if the attributes are defined for the element.

---

**`__getitem__(attr)`** :&#8658; `str`

> Gets an attribute of the element, looking first at the tag attributes and then javascript attributes of the element

> Parameters:
> * `attr`: `str`
> 	* The name of the attribute

> Notes:
> * Where `Hit.__getattr__(attr)` raises an `AttributeError` if the attribute isn't present, this method will return `None`

---

**`apply(method)`** :&#8658; Any

> Applies a method to the element

> Parameters:
> * `method`: `Callable(Element)`:&#8658; Any
> 	* The function to call with the element as input

---

**`click()`**

> Clicks the element

---

**`hide()`**

> Hides the element if it is displayed

---

**`if_(condition)`** :&#8658; `Hit`, `Miss`

> Checks a condition or applies one to this element, returning the element or a `Miss`

> Parameters:
> * `condition`: `bool`, `Callable(Element)` :&#8658; `bool`
> 	The condition to check or apply

---

**`reset_display()`**

> Resets the display to it's original state if the property was present

---

**`screenshot(mode)` :&#8658; `str`, `bytes`, `PIL.Image.Image`**

> Takes a screenshot of the element

> Parameters:
> * `mode`: `str` = `'png'`
> 
>   * One of: 'base64', 'png', 'image'

> Notes:
> * Currently this is only available in Chrome

---

**`verify(condition)`** :&#8658; `bool`

> Checks a condition or applies one to this element returning the result

> Parameters:
> * `condition`: `bool`, `Callable(Element)` :&#8658; `bool`
> 	The condition to check or apply

<br>
<br>

# 4. `Timelapse`

A wrapper around `timelapse.js`

<br>

---

## 4.1. Examples

---

```py
>>> from selenium.webdriver import Chrome
>>> from timelapse import Timelapse
>>> 
>>> driver = Chrome('drivers/chromedriver.exe')
>>> driver.get('https://earthtime.org/explore')
>>> 
>>> timelapse = Timelapse(driver)
>>> 
>>> timelapse.getCaptureTimes()
["1984", "1985", "1986", "1987", "1988", "1989", "1990", "1991", "1992", "1993", "1994", "1995", "1996", "1997", "1998", "1999", "2000", "2001", "2002", "2003", "2004", "2005", "2006", "2007", "2008", "2009", "2010", "2011", "2012", "2013", "2014", "2015", "2016", "2017", "2018", "2019"]
>>> 
>>> driver.quit()
```

<br>

---

## 4.2. Methods

---

**`__init__(driver)`**

> Parameters:
> * `driver` : `WebDriver`
> 
> 	* A running **Selenium** `WebDriver`

---

**`__getattr__(name)`**

> Gets the attribute `name` in `timelapse.js` if one exists. If `name` refers to a function, it is transformed into a lambda expression.

> Parameters:
> * `name` : `str`
> 
> 	* The name of the attribute

<br>
<br>

# 5. `Environment`

An `Environment` is the standard way of controlling an **EarthTime** webpage. It provides the easiest means of accessing and handling of elements within the DOM.

Their are two types of environments:

* `Environment`
  * The main class that defines all the behavior
  
* `CachedEnvironment`
  * The same as `Environment` but the index-access is cached

<br>

---

## 5.1. Examples

---

Note examples do not show screenshots and the element ids will change with each instance

*Assumes the following import*

```py
>>> from unearthtime.environment import Environment
```

<br>

### 5.1.1. Instantiation

```py
>>> env = Environment()
>>> env.activate()
>>> env.quit()
>>> 
>>> env = Environment.explore()
>>> env.quit()
>>> 
>>> with Environment() as env:
...		pass
...
>>> 
>>> env = Environment('https://earthtime.org/stories/sahel_in_peril')
>>> env.activate()
>>> driver = env.release_driver()
>>> 
>>> env = Environment.explore('https://earthtime.org/stories/sahel_in_peril', driver)
>>> env.quit()
>>> 
>>> with Environment.explore('https://earthtime.org/stories/sahel_in_peril'):
...   pass
...
>>>
```

<br>

### 5.1.2. Element access

```py
>>> env = Environment.explore()
>>> 
>>> env['EarthTimeLogo']
Hit[265876ba-64eb-4dda-971f-3bb1d4db9542]
>>> 
>>> env['StoriesMenu']
Hit[74c6226f-cc5a-495e-a0cf-7c8e9b78a1f0]
>>> 
>>> env['ThemeHeaders']
Miss
>>>
>>> env['StoriesMenu'].click()
>>> env['ThemeHeaders']
HitList[
        Hit[644afca9-7350-42d9-9eda-5ceb3777f4df]
        Hit[10446881-091f-4a65-a445-12464994ec7b]
        Hit[f453b7fe-478e-4dab-8d75-c9dd92ea05bd]
        Hit[4949eae0-8c4f-40d3-83af-c498ee3b1ef4]
        Hit[deadc66b-8434-45c7-8d1f-17fbf5a79fee]
        Hit[53cb03b9-ea1e-4058-adc7-f3b1c9b04346]
        Hit[a6393254-a080-4d4c-a337-e660ac666a87]
        Hit[4220aa8a-cfd1-4664-a2df-a24145a01815]
]
>>> 
>>> # Close Story Menu
>>> env['StoriesMenu'].click()
>>> 
>>> # Getting Theme Headers, clicking the Stories Menu if it isn't open
>>> env.repeat_if('ThemeHeaders', actions=lambda: env['StoriesMenu'].click())
HitList[
        Hit[644afca9-7350-42d9-9eda-5ceb3777f4df]
        Hit[10446881-091f-4a65-a445-12464994ec7b]
        Hit[f453b7fe-478e-4dab-8d75-c9dd92ea05bd]
        Hit[4949eae0-8c4f-40d3-83af-c498ee3b1ef4]
        Hit[deadc66b-8434-45c7-8d1f-17fbf5a79fee]
        Hit[53cb03b9-ea1e-4058-adc7-f3b1c9b04346]
        Hit[a6393254-a080-4d4c-a337-e660ac666a87]
        Hit[4220aa8a-cfd1-4664-a2df-a24145a01815]
]
>>> 
>>> # Get the Theme Headers without the overhead
>>> env.findall("div.themes-div > h3[data-enabled='true']")
HitList[
        Hit[644afca9-7350-42d9-9eda-5ceb3777f4df]
        Hit[10446881-091f-4a65-a445-12464994ec7b]
        Hit[f453b7fe-478e-4dab-8d75-c9dd92ea05bd]
        Hit[4949eae0-8c4f-40d3-83af-c498ee3b1ef4]
        Hit[deadc66b-8434-45c7-8d1f-17fbf5a79fee]
        Hit[53cb03b9-ea1e-4058-adc7-f3b1c9b04346]
        Hit[a6393254-a080-4d4c-a337-e660ac666a87]
        Hit[4220aa8a-cfd1-4664-a2df-a24145a01815]
]
>>> 
>>> env.find("div.themes-div > h3[data-enabled='true']")
Hit[644afca9-7350-42d9-9eda-5ceb3777f4df]
>>> 
>>> 
>>> def actions():
...   env['StoriesMenu'].click()
...   header = env['ThemeHeader', 'crisis_in_the_sahel'].click()
... 
...   if header['aria-selected'] == 'false':
...     header.click()
... 
>>> 
>>> env.repeat_if(('ThemeStories', 'crisis_in_the_sahel'), actions=actions)
HitList[
        Hit[2d529009-a887-4973-98d2-3d24433235d8]
        Hit[c758eb7a-eb11-4b04-87c8-12f244737903]
        Hit[f8ddf8cd-c69b-48a4-92da-66d1d3099aa7]
]
>>>
>>> env['LegendContainer']
Miss
>>> 
>>> env.find('layers-legend')
Miss
>>> 
>>> env.find('layers-legend', By.ID)
Hit[98616ee2-2d01-4697-b377-7804f723f67c]
>>> 
>>> # Using visibility of element wait condition
>>> from selenium.webdriver.support import expected_conditions as EC
>>> 
>>> env.find('layers-legend', By.ID, EC.visibility_of)
Miss
>>> 
>>> env.quit()
```

  **Note**
  
  *In some cases an element is associated with several `Locator`s and/or `terms`. What happens in this case is `Environment` will cycle through them until it reaches a successful `Hit` or `HitList`, otherwise a `Miss` will be returned.* 
  
  *If an element has multiple `Locator`s, this behavior can be overridden by specifying the zero-based index of the exact `Locator` to use. If an element has several locators priority of attributes if present are 'id', 'class', others. E.g. `ThemeHeader` can be located by it's 'id' or 'aria-controls' attribute. The locators will be ordered ['id', 'aria-controls']*

  *If an element has multiple `terms`, either a single `By` can be passed in to be used for each one, or a `By` for each `term`. Arguments are different, if several `terms` are callable then it is assumed that they all have matching signatures. If this is not the case, all callable `terms` should be specified so thay they do.*


<br>

### 5.1.3. Page Interaction

```py
>>> env = Environment.explore('https://earthtime.org/stories/sahel_in_peril')
>>> 
>>> env['Waypoints']
HitList[
        Hit[583e5543-31ce-4f56-a4e9-cd7a802bd9a4]
        Hit[170a9bcf-73cc-47bc-b53c-9023b79924ff]
        Hit[4b813513-e0ba-4767-a299-d819cb9bb16f]
        Hit[0cf707a7-10cb-4488-b05f-1cda45d252a2]
        Hit[260b2ef5-9a3c-4a05-9e2c-a222acc23d8b]
        Hit[151efc2d-4f30-4063-856c-c14f7d116ef6]
        Hit[83c2fbca-9605-4b39-9b2c-a35363f25e20]
        Hit[6e1313ec-489f-4c0c-ab1a-4a83831511a2]
        Hit[cb729c86-9f86-4a37-8fa1-c64fa2e3fadd]
        Hit[b071fbc5-3cc6-4b46-9a88-180f1ff581b0]
        Hit[02752be6-d841-44de-a975-433f2d9e2ea3]
        Hit[75e1a330-db1c-41f0-b943-203d147e23ea]
        Hit[41b54f4b-af3f-4b52-b5c2-497ed9c4748f]
        Hit[bc03e58c-f54b-4c0e-9cfb-0c7a15725515]
        Hit[4f619620-e327-4512-a185-05bd3e717b68]
        Hit[48470ba2-38f4-48ec-8563-62f56fbfad89]
        Hit[b766c96c-2332-426e-9ce8-26b9731f1ca1]
]
>>> env['Waypoints'][1].id_
'Context'
>>> 
>>> env['Waypoints'][1].click()
>>> 
>>> wid = env['Waypoints'][4].id_
>>> 
>>> env['Waypoint', wid]
Hit[260b2ef5-9a3c-4a05-9e2c-a222acc23d8b]
>>> 
>>> env['Waypoint', wid].click()
>>> 
```

**Note**

*Interactions that cause the page to be navigated away from or reloaded -- clicking the logo, refreshing the page, using back or forward -- will invalidate any elements previously accessed as it resets the session of the page*

*For this reason `Environment` does not provide a way to do this directly, except for cases resulting from element interaction, e.g. clicking the logo. Interactions like refreshing the page, going back or forward, navigating to a different page can be directly done through the `WebDriver` associated with the environment*

*This does not apply to clicking on waypoints*

```py
>>> logo = env['EarthTimeLogo']
>>> logo.click()
>>> 
>>> env.current_url
'https://earthtime.org/'
>>> 
>>> env.driver.back()
>>> 
>>> logo.click()
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "C:\Users\hjhaw\source\create\dev\unearthtime\unearthtime\explore\response.py", line 81, in click
    super().click()
  File "C:\Users\hjhaw\source\create\dev\unearthtime\unearthtime\.venv\lib\site-packages\selenium\webdriver\remote\webelement.py", line 80, in click
    self._execute(Command.CLICK_ELEMENT)
  File "C:\Users\hjhaw\source\create\dev\unearthtime\unearthtime\.venv\lib\site-packages\selenium\webdriver\remote\webelement.py", line 633, in _execute
    return self._parent.execute(command, params)
  File "C:\Users\hjhaw\source\create\dev\unearthtime\unearthtime\.venv\lib\site-packages\selenium\webdriver\remote\webdriver.py", line 321, in execute
    self.error_handler.check_response(response)
  File "C:\Users\hjhaw\source\create\dev\unearthtime\unearthtime\.venv\lib\site-packages\selenium\webdriver\remote\errorhandler.py", line 242, in check_response
    raise exception_class(message, screen, stacktrace)
selenium.common.exceptions.StaleElementReferenceException: Message: stale element reference: element is not attached to the page document
  (Session info: chrome=83.0.4103.97)

>>> logo
Hit[e06d06a3-34d5-4254-88f2-77b1f21a6a37]
>>> 
>>> env.get('EarthTimeLogo')
Hit[d8a05059-7623-4d84-9a4d-b9c4e93df003]
>>> 
>>> env.quit()
```

<br>

---

## 5.2. Properties

---

**`driver` :&#8658; `WebDriver`**
> The **Selenium** `WebDriver` associated with this `Environment`

**`title` :&#8658; `str`**
> The title of the page

**`url` :&#8658; `str`**
> The current url of the page

<br>

---

## 5.3. Methods

---

**`__init__([url][, driver])`**

> Parameters:  
> * `url` : `str` = 'https://earthtime.org/explore'
> 	* An optional string of the form *'https://[name].earthtime.org/[explore | stories/[story]]'*
> 
> * `driver`: `WebDriver`, `Callable()` &#8658; `WebDriver` = `lambda: selenium.webdriver.Chrome('drivers/chromedriver.exe')`
> 	* An optional **Selenium** `WebDriver` or a zero-arg function that returns a `WebDriver`

> Raises:  
> * `UnearthtimeException`  
> 
> 	* If `url` is malformed or not an accepted **EarthTime** page
> 	* If `driver` is associated with another `Environment`
> 
> * `TypeError`
> 	* If `driver` is not of an accepted type

---

**`@classmethod`**  
**`explore([url][, driver])`** :&#8658; `Environment`

> Activates the environment before returning it

> Parameters:  
> * `url` : `str` = 'https://earthtime.org/explore'
> 	* An optional string of the form *'https://[name].earthtime.org/[explore | stories/[story]]'*
> 
> * `driver`: `WebDriver`, `Callable()` &#8658; `WebDriver` = `lambda: selenium.webdriver.Chrome('drivers/chromedriver.exe')`
> 	* An optional **Selenium** `WebDriver` or a zero-arg function that returns a `WebDriver`

---

**`__getattr__(name)` :&#8658; `Hit`, `HitList`, `Miss` or `Any`, `None`**

> Depending on what `name` represents it will return the result of a `Locator` or whatever is represented by executing the javascript statement `return timelapse.[name]`
>   * If `name` represents a function, i.e. `timelapse.[name]` is a function, it will be converted into a lambda expression accepting the same number of arguments.

---

**`__getitem__(key)` :&#8658; `Hit`, `HitList`, `Miss`**

> Attempts to retrieve an element or elements of the provided `Locator` name, caching the result of the query
> 
> Parameters:
> * `key`: `str`, `tuple`
>   * The name of a predefined `Locator` or a tuple containing the name and any arguments needed for its `Locator`(s) or their `term`(s)
> 
>   * To override the wait condition associated with a `Locator` if one is, or simply provide one, either the last or second-to-last if an index is provided element of the tuple must be a `Callable(WebDriver)` :&#8658; `Hit`, `HitList`, `False`
> 
>   * Optionally, the last argument can also be an `int` specifying which `Locator` to use in the cases when a name has several, e.g. `ThemeHeader` can be accessed either using it's *id* or *aria-controls* attribute

> Notes:
> * To perform a "fresh" query against the DOM the `get` method should be used. 
> * The `invalidate` method can be used to clear and invalidate the query cache. See `Environment` note 2.

---

**`activate([imp_wait])`**

> Instantiates the `WebDriver` of this environment if necessary, then loads the page associated with the given url. The page will be maximized automatically

> Parameters:
> * `imp_wait`: `int` = 0
> 
>   * An implicit wait time in seconds to be used by the driver every time it tries to access an element and fails. It tells the driver how long to poll the DOM when trying to find an element or elements. The `implicitly_wait` method can be used to change this value

---

**`execute(javascript[, *args])` :&#8658; `Any`, `None`**

> Executes a string of javascript with the provided arguments

> Parameters:
> * `javascript` : `str`
>   * Semicolon separated javascript statements
> 
> * `*args`
>   * An optional list of arguments to be used when executing the statement(s). Arguments can appear in the `javascript` string using the form *'arguments[n]'*, where *'n'* is the zero-based index of the argument in the `*args` list

---

**`find(query[, by][, until])`** :&#8658; `Hit`, `HitList`, `Miss`

> Attempts locate an element in the DOM satisfying a query

> Parameters:
> * `query` : `str`
>   * The string to search for
> 
> * `by` : `By` = `By.CSS`
>   * What `query` is supposed to represent
> 
> * `until` : `Callable(WebDriver)` :&#8658; `Hit`, `HitList`, `False`

---

**`findall(query[, by][, until])`** :&#8658; `Hit`, `HitList`, `Miss`

> Attempts locate all elements in the DOM satisfying a query

> Parameters:
> * `query` : `str`
>   * The string to search for
> 
> * `by` : `By` = `By.CSS`
>   * What `query` is supposed to represent
> 
> * `until` : `Callable(WebDriver)` :&#8658; `Hit`, `HitList`, `False`

---

**`fullscreen()`**

> Makes the window fullscreen

---

**`get(key)` :&#8658; `Hit`, `HitList`, `Miss`**

> Attempts to retrieve an element or elements of the provided `Locator` name

> Parameters:
> * `key`: `str`, `tuple`
>   * The name of a predefined `Locator` or a tuple containing the name and any arguments needed for its `Locator`(s) or their `term`(s)
> 
>   * To override the wait condition associated with a `Locator` if one is, or simply provide one, either the last or second-to-last if an index is provided element of the tuple must be a `Callable(WebDriver)` :&#8658; `Hit`, `HitList`, `False`
> 
>   * Optionally, the last argument can also be an `int` specifying which `Locator` to use in the cases when a name has several, e.g. `ThemeHeader` can be accessed either using it's *id* or *aria-controls* attribute

---

**`implicitly_wait(time)`**

> Sets the amount of time for the driver to poll the DOM when finding an element

> Parameters:
> * `time` : `int`  
>   * The number of seconds to poll DOM 

---

**`invalidate()`**

> Clears and invalidates the query cache of this environment. Useful for when cached elements are no longer valid for the DOM of the current page

---

**`is_active()` :&#8658; `bool`**

> Whether or not the environment is still connected to a driver

---

**`maximize()`**

> Maximizes the window

---

**`minimize()`**

> Minimizes the window

---

**`position()` :&#8658; `dict`**

> The position of the window relative to the left side (`x`) and top (`y`) of the screen

---

**`pause_at_end()`**

> Pauses the timeline and sets it to the end

---

**`pause_at_start()`**

> Pauses the timeline and sets it to the beginning

---

**`quit()`**

> Deactivates the environment and quits the driver

---

**`release_driver()`** :&#8658; `WebDriver`

> Deactivates the environment returning the running driver

---

**`screenshot(mode)` :&#8658; `str`, `bytes`, `PIL.Image.Image`**

> Takes a screenshot

> Parameters:
> * `mode`: `str` = `'png'`
> 
>   * One of: 'base64', 'png', 'image'

---

**`screenshot_and_save(path)`**

> Takes a screenshot and saves it

> Parameters:
> * `path`: `str`
>   * The path to save the image to

---

**`size()` :&#8658; `dict`**

> The `width` and `height` of the window

---

**`thumbnail([width][, height])`** : &#8658; `Thumbnail`

> A thumbnail of the current view as defined by the methods `Timelapse.getThumbnailOfCurrentView` or `Timelapse.getThumbnailOfView`

> Parameters:
> * `width` : `int`, `float`, `AspectRatio`, `None` = `640`
>   * The width of the thumbnail expressed directly or as a ratio width-to-height
> 
> * `height` : `int`, `float`, `AspectRatio`, `None` = `320`
>   * The height of the thumbnail expressed directly or as a ratio height-to-width

---


