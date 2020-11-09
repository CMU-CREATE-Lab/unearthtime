import concurrent.futures
from functools import partial
from typing import Union

from .response import ConcurrentHit, ConcurrentHitList
from .._algae.exceptions import UnearthtimeException
from ..earthtime import _ImplicitWait, DriverType, EarthTime
from ..explore.response import Hit, HitList


class ConcurrentEarthtime:
    
    def __init__(self, driver: DriverType, *urls: str):
        self.__pool = []
        self.__exc = None
        self.__driver = driver
        
        if urls:
            self.__urls = urls
        else:
            raise UnearthtimeException('Expected at least one EarthTime url.')
        self.__running = False
    
    def __bool__(self):
        return all(self.__pool)
    
    def __call__(self, fn, *args, **kwargs):
        res = list(self.__exc.map(lambda et: f(*args, **kwargs) if callable(
            (f := et.__getattribute__(fn))) else f, self.__pool))
        
        if isinstance(res[0], Hit):
            return ConcurrentHit(*res)
        elif isinstance(res[0], HitList):
            return ConcurrentHitList(*res)
        else:
            return res
    
    def __enter__(self):
        if not self.__running:
            self.load()
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.quit()
    
    def __getattr__(self, name):
        f = self.__pool[0].__getattribute__(name)
        
        if callable(f):
            return partial(self.__call__, name)
        else:
            return list(self.__exc.map(lambda et: et.__getattribute__(name)))
    
    def __getitem__(self, key: Union[int, str, tuple]):
        if isinstance(key, int):
            if -len(self.__pool) <= key < len(self.__pool):
                return self.__pool[key]
            else:
                raise IndexError(f':[{key}]: Invald index for pool of size {len(self.__pool)}.')
        elif isinstance(key, tuple) and isinstance(key[-1], bool):
            return self.__call__('pull', key[:-1], key[-1])
        else:
            return self.__call__('pull', key)
    
    def __len__(self):
        return len(self.__pool)
    
    @property
    def pages(self):
        return self.__pool
    
    def is_running(self):
        return self.__running and all(self.__exc.map(lambda et: et.is_running(), self.__pool))
    
    def load(self, load_wait: Union[float, int] = 0, imp_wait: Union[float, int] = _ImplicitWait):
        if not self.__running:
            self.__exc = concurrent.futures.ThreadPoolExecutor(max_workers=len(self.__urls))
            self.__pool = list(self.__exc.map(
                lambda url: EarthTime.explore(self.__driver, url, load_wait, imp_wait),
                self.__urls))
            self.__running = True
    
    def quit(self):
        self.__exc.map(lambda et: et.quit(), self.__pool)
        self.__exc.shutdown()
        self.__running = False
        self.__pool = []
    
    def shutdown(self):
        self.__exc.shutdown()
        self.__running = False
        pool = self.__pool
        self.__pool = []
        
        return pool
    
    def screenshot_and_save(self, *fps: str, color_space: str = 'RGB', format_=None, **params):
        args = [(et, fp, color_space, format_, params) for et, fp in zip(self.__pool, fps)]
        _ = list(self.__exc.map(lambda arg: arg[0].screenshot_and_save(*arg[1:4], **arg[4]), args))
    
    def screenshot_map_and_save(self, *fps: str, color_space: str = 'RGB', format_=None, **params):
        
        args = [(et, fp, color_space, format_, params) for et, fp in zip(self.__pool, fps)]
        _ = list(self.__exc.map(lambda arg: arg[0].screenshot_map_and_save(*arg[1:4], **arg[4]), args))
