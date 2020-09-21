from __future__ import annotations

from collections import ChainMap

from .locator import Locator

from typing import Dict, Iterable, Tuple, Union

LocatorReference = Union[Dict[str, Locator], Iterable[Tuple[str, Locator]]]


class Registry:

    def __init__(self, locators: LocatorReference = None):

        if locators:
            if isinstance(locators, dict):
                self.__dictionary = ChainMap({key: value for key, value in locators.items() if isinstance(key, str) and isinstance(value, Locator)})
            elif isinstance(locators, Iterable):
                self.__dictionary = ChainMap({pair[0]: pair[1] for pair in locators if isinstance(pair[0], str) and isinstance(pair[1], Locator)})
            else:
                self.__dictionary = ChainMap()

    def __contains__(self, key: str): return key in self.__dictionary

    def __getitem__(self, key: str): return self.__dictionary[key] if key in self.__dictionary else None

    def __iter__(self):
        for key in sorted(self.__dictionary.keys()):
            yield self.__dictionary[key]

    def __len__(self): return len(self.__dictionary.keys())

    def __reversed__(self):
        for key in reversed(sorted(self.__dictionary.keys())):
            yield self.__dictionary[key]

    def __setitem__(self, key: str, locator: Locator): self.__dictionary[key] = locator

    def __delitem__(self, key: str):
        for map_ in self.__dictionary.maps:
            if key in map_:
                del map_[key]
                break

    @property
    def registers(self): return self.__dictionary.maps

    def all_for(self, key: str): return [map_[key] for map_ in self.__dictionary.maps if key in map_]

    def clean(self):
        maps = self.__dictionary.maps
        for i in range(len(maps)):
            if not bool(maps[i]):
                del maps[i]

        if not maps:
            self.__dictionary.maps.append({})


    def delete(self, key: str):
        for map_ in self.__dictionary.maps:
            if key in map_:
                del map_[key]
                break

    def delete_all(self, key: str):
        for map_ in self.__dictionary.maps:
            if key in map_:
                del map_[key]

    def first_for(self, key: str):
        for map_ in self.__dictionary.maps:
            if key in map_:
                return map_[key]

    def last_for(self, key: str):
        for map_ in reversed(self.__dictionary.maps):
            if key in map_:
                return map_[key]

    def overwrite(self, key: str, locator: Locator):
        for map_ in self.__dictionary.maps:
            if key in map_:
                map_[key] = locator
                break

    def register(self, locators: LocatorReference):
        if isinstance(locators, dict):
            new_dict = {key: locator for key, locator in locators if isinstance(key, str) and isinstance(locator, Locator)}
        elif isinstance(locators, Iterable):
            new_dict = {pair[0]: pair[1] for pair in locators if isinstance(pair[0], str) and isinstance(pair[1], Locator)}
        else:
            new_dict = {}

        if new_dict:
            self.__dictionary.maps[0:0] = [new_dict]

    def register_last(self, locators: LocatorReference):
        if isinstance(locators, dict):
            new_dict = {key: locator for key, locator in locators if isinstance(key, str) and isinstance(locator, Locator)}
        elif isinstance(locators, Iterable):
            new_dict = {pair[0]: pair[1] for pair in locators if isinstance(pair[0], str) and isinstance(pair[1], Locator)}
        else:
            new_dict = {}

        if new_dict:
            self.__dictionary.maps.append(new_dict)

    def search(self, pattern: str): return [key for key in self.__dictionary.keys() if pattern in key]

    def update(self, key: str, locator: Locator):
        if key not in self.__dictionary.maps[0]:
            self.__dictionary[key] = locator
        else:
            self.__dictionary.maps[0:0] = [{key: locator}]