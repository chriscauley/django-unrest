from functools import wraps
import os
import json
import time

def mkdir(root, *args):
    parts = os.path.join(*args).strip('/').split('/')
    path = root
    if not os.path.exists(path):
        os.mkdir(path)
    for part in parts:
        path = os.path.join(path, part)
        if not os.path.exists(path):
            os.mkdir(path)
    return path


class JsonCache(dict):
    def __init__(self, path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._path = path
        if os.path.exists(self._path):
            with open(self._path, 'r') as f:
                self.update(json.loads(f.read()))
    def __setitem__(self, key, value):
        if callable(value):
            if not key in self:
                super().__setitem__(key, value())
        else:
            super().__setitem__(key, value)
        self._save()
    def _save(self):
        with open(self._path, 'w') as f:
            f.write(json.dumps(self, indent=2))

def _ms(seconds):
    if seconds <10:
        return round(seconds * 1000,3)
    return int(seconds * 1000)

def time_it(func, verbose=False):
    if func == True:
        return lambda func: time_it(func, verbose=True)
    times = []
    @wraps(func)
    def wrapped(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        dt = time.time()-start
        times.append(dt)
        if verbose:
            ave = _ms(sum(times) / len(times))
            _sum = _ms(sum(times))
            print(func.__name__, _ms(dt), ave, _sum)
        return result
    def _print():
        ave = _ms(sum(times) / len(times))
        _sum = _ms(sum(times))
        print(f'{func.__name__} ave={ave} total={_sum} count={len(times)}')
    wrapped.print = _print
    return wrapped

class Ticker:
    def __init__(self, name=None):
        self.name = name
        self.last = self.start = time.time()
        self.counts = 0
    def __call__(self):
        self.counts += 1
        _now = time.time()
        dt = _ms(_now - self.last)
        s = f'{name}\tdt={dt}'
        # if new_name == self.name:
        #     ave = _ms(_now - self.start) // self.counts)
        #     s += f'\tave={ave}\tcounts={counts}'
        # else:
        #     self.name = new_name
        #     self.counts = 0
        print(s)
