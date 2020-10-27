from concurrent.futures import ThreadPoolExecutor
from functools import partial
from itertools import chain
from typing import Union

from selenium.webdriver.remote.webelement import WebElement as Element


class ConcurrentHit:
    
    def __init__(self, *hits: Element):
        self.__hits = hits
        self.__exc = ThreadPoolExecutor(max_workers=len(hits))
        
    def __call__(self, fn, *args, **kwargs):
        return list(self.__exc.map(lambda hit: f(*args, **kwargs) if callable(
            (f := hit.__getattribute__(fn))) else f, self.__hits))
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
    
    def __getattr__(self, name):
        f = self.__hits[0].__getattribute__(name)
        
        if callable(f):
            return partial(self.__call__, name)
        else:
            return list(self.__exc.map(lambda hit: hit.__getattribute__(name), self.__hits))
        
    def __getitem__(self, key: Union[int, str]):
        if isinstance(key, int):
            if -len(self.__pool) <= key < len(self.__pool):
                return self.__pool[key]
            else:
                raise IndexError(f':[{key}]: Invald index for pool of size {len(self.__pool)}.')
        else:
            return list(self.__exc.map(lambda hit: hit[key], self.__hits))
    
    @property
    def hits(self):
        return self.__hits
        
    def screenshot_and_save(self, *fps, color_space: str = 'RGB', format_=None, **params):
        args = [(hit, fp, color_space, format_, params) for hit, fp in zip(self.__hits, fps)]
        _ = list(self.__exc.map(lambda arg: arg[0].screenshot_and_save(*arg[1:4], **arg[4]), args))
        
    def shutdown(self):
        self.__exc.shutdown()
        self.__exc = None
        return self.__hits


class ConcurrentHitList:
    
    def __init__(self, *hitlists: Element):
        self.__hitlists = hitlists
        self.__exc = ThreadPoolExecutor(max_workers=len(hitlists))
    
    def __call__(self, fn, *args, **kwargs):
        return list(self.__exc.map(lambda hit: f(*args, **kwargs) if callable(
            (f := hit.__getattribute__(fn))) else f, chain(self.__hitlists)))
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.shutdown()
    
    def __getattr__(self, name):
        f = self.__hitlists[0][0].__getattribute__(name)
        
        if callable(f):
            return partial(self.__call__, name)
        else:
            return list(self.__exc.map(lambda hit: hit.__getattribute__(name), self.__hits))
    
    def __getitem__(self, key: int):
        if -len(self.__pool) <= key < len(self.__pool):
            return self.__pool[key]
        else:
            raise IndexError(f':[{key}]: Invald index for pool of size {len(self.__pool)}.')
    
    @property
    def hitlists(self):
        return self.__hitlists
    
    def shutdown(self):
        self.__exc.shutdown()
        self.__exc = None
        return self.__hitlists