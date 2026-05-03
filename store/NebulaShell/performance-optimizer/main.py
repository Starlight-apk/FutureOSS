import sys
import time
import functools
from typing import Any, Callable, Optional, TypeVar, Generic, Dict, List, Set
from collections import deque
from dataclasses import dataclass, field
from threading import Lock
import weakref

T = TypeVar('T')
F = TypeVar('F', bound=Callable)


class FastCache:
    __slots__ = ('_cache', '_order', '_maxsize', '_ttl', '_hits', '_misses', '_lock')
    
    def __init__(self, maxsize: int = 1024, ttl: float = 0):
        self._cache: Dict[Any, Any] = {}
        self._order: deque = deque()
        self._maxsize = maxsize
        self._ttl = ttl
        self._hits = 0
        self._misses = 0
        self._lock = Lock() if sys.version_info < (3, 9) else None
    
    def get(self, key: Any) -> tuple[bool, Any]:
        if key not in self._cache:
            self._misses += 1
            return False, None
        
        entry = self._cache[key]
        if self._ttl > 0 and time.time() - entry[1] > self._ttl:
            del self._cache[key]
            try:
                self._order.remove(key)
            except ValueError:
                pass
            self._misses += 1
            return False, None
        
        self._order.remove(key)
        self._order.append(key)
        self._hits += 1
        return True, entry[0]
    
    def set(self, key: Any, value: Any):
        if key in self._cache:
            self._order.remove(key)
        self._cache[key] = (value, time.time())
        self._order.append(key)
        if len(self._cache) > self._maxsize:
            oldest = self._order.popleft()
            del self._cache[oldest]
    
    def clear(self):
        self._cache.clear()
        self._order.clear()
        self._hits = 0
        self._misses = 0
    
    @property
    def hit_rate(self) -> float:
        total = self._hits + self._misses
        if total == 0:
            return 0.0
        return self._hits / total


def cached(maxsize: int = 1024, ttl: float = 0, key_func: Callable = None):
    _cache = FastCache(maxsize=maxsize, ttl=ttl)
    
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                key = (args, tuple(sorted(kwargs.items())))
            
            hit, value = _cache.get(key)
            if hit:
                return value
            
            value = func(*args, **kwargs)
            _cache.set(key, value)
            return value
        
        wrapper.cache = _cache
        wrapper.cache_clear = _cache.clear
        wrapper.cache_stats = _cache.stats
        return wrapper
    return decorator


class ObjectPool(Generic[T]):
    __slots__ = ('_factory', '_pool', '_maxsize', '_created', '_acquired', '_lock')
    
    def __init__(self, factory: Callable[[], T], maxsize: int = 100):
        self._factory = factory
        self._pool: List[T] = []
        self._maxsize = maxsize
        self._created = 0
        self._acquired = 0
        self._lock = Lock() if sys.version_info < (3, 9) else None
    
    def acquire(self) -> T:
        if self._pool:
            obj = self._pool.pop()
        else:
            obj = self._factory()
            self._created += 1
        self._acquired += 1
        return obj
    
    def release(self, obj: T):
        if len(self._pool) < self._maxsize:
            self._pool.append(obj)
    
    def clear(self):
        self._pool.clear()


class BatchProcessor(Generic[T]):
    __slots__ = ('_handler', '_batch_size', '_timeout', '_buffer', '_last_flush', '_processed_count')
    
    def __init__(self, batch_handler: Callable[[List[T]], Any], batch_size: int = 100, timeout: float = 1.0):
        self._handler = batch_handler
        self._batch_size = batch_size
        self._timeout = timeout
        self._buffer: List[T] = []
        self._last_flush = time.time()
        self._processed_count = 0
    
    def add(self, item: T):
        self._buffer.append(item)
        if len(self._buffer) >= self._batch_size:
            self.flush()
    
    def flush(self):
        if not self._buffer:
            return
        
        self._handler(self._buffer)
        self._buffer.clear()
        self._last_flush = time.time()
        self._processed_count += 1
    
    @property
    def pending_count(self) -> int:
        return len(self._buffer)
    
    def stats(self) -> dict[str, Any]:
        return {
            "pending": len(self._buffer),
            "batch_size": self._batch_size,
            "flush_count": self._processed_count,
        }


class MemoryArena:
    __slots__ = ('_data', '_free_list', '_allocated', '_total_size')
    
    def __init__(self, size: int = 1024 * 1024):
        self._data = bytearray(size)
        self._free_list: List[tuple[int, int]] = [(0, size)]
        self._allocated: Set[int] = set()
        self._total_size = size
    
    def allocate(self, size: int) -> Optional[memoryview]:
        for i, (offset, block_size) in enumerate(self._free_list):
            if block_size >= size:
                self._free_list.pop(i)
                if block_size > size:
                    self._free_list.append((offset + size, block_size - size))
                self._allocated.add(offset)
                return memoryview(self._data)[offset:offset + size]
        return None
    
    def deallocate(self, view: memoryview):
        offset = view.obj.__array_interface__['data'][0] - id(self._data) if hasattr(view.obj, '__array_interface__') else 0
        if offset in self._allocated:
            self._allocated.remove(offset)
            self._free_list.append((offset, len(view)))
    
    @property
    def available(self) -> int:
        return sum(size for _, size in self._free_list)
    
    @property
    def usage_rate(self) -> float:
        return 1.0 - (self.available / self._total_size)


class HotPathOptimizer:
    __slots__ = ('_call_counts', '_threshold', '_optimized', '_start_times')
    
    def __init__(self, threshold: int = 1000):
        self._call_counts: Dict[str, int] = {}
        self._threshold = threshold
        self._optimized: Set[str] = set()
        self._start_times: Dict[str, float] = {}
    
    def track(self, func_name: str):
        self._call_counts[func_name] = self._call_counts.get(func_name, 0) + 1
        if self._call_counts[func_name] >= self._threshold and func_name not in self._optimized:
            self._optimized.add(func_name)
            return True, self._call_counts[func_name]
        return False, self._call_counts[func_name]


class PerfProfiler:
    __slots__ = ('_records', '_stack', '_enabled')
    
    def __init__(self):
        self._records: Dict[str, List[float]] = {}
        self._stack: List[tuple[str, float]] = []
        self._enabled = True
    
    def start(self, name: str):
        if not self._enabled:
            return
        self._stack.append((name, time.perf_counter()))
    
    def stop(self, name: str):
        if not self._enabled or not self._stack:
            return
        
        top_name, start_time = self._stack.pop()
        if top_name != name:
            return
        
        elapsed = time.perf_counter() - start_time
        if name not in self._records:
            self._records[name] = []
        self._records[name].append(elapsed)
    
    def context(self, name: str):
        pass


class StringIntern:
    __slots__ = ('_cache',)
    
    def __init__(self, use_weak_refs: bool = True):
        self._cache: Dict[str, str] = {}
    
    def intern(self, s: str) -> str:
        if s in self._cache:
            return self._cache[s]
        
        import sys
        interned = sys.intern(s)
        self._cache[interned] = interned
        
        return interned
    
    def clear(self):
        self._cache.clear()


class PerformanceOptimizerPlugin:
    def __init__(self):
        self._initialized = False
        self._caches: Dict[str, FastCache] = {}
        self._pools: Dict[str, ObjectPool] = {}
        self._profiler = PerfProfiler()
        self._hot_path = HotPathOptimizer()
        self._string_intern = StringIntern()

    def init(self, deps: dict = None):
        if self._initialized:
            return
        
        self._caches["route_match"] = FastCache(maxsize=2048)
        self._caches["path_params"] = FastCache(maxsize=2048)
        self._caches["template_render"] = FastCache(maxsize=512)
        
        self._pools["bytearray_4k"] = ObjectPool(lambda: bytearray(4096), maxsize=100)
        self._pools["bytearray_64k"] = ObjectPool(lambda: bytearray(65536), maxsize=20)
        
        self._initialized = True
    
    def start(self):
        pass
    
    def stop(self):
        for cache in self._caches.values():
            cache.clear()
        for pool in self._pools.values():
            pool.clear()
        self._profiler = PerfProfiler()
    
    def get_cache(self, name: str) -> Optional[FastCache]:
        return self._caches.get(name)
    
    def get_pool(self, name: str) -> Optional[ObjectPool]:
        return self._pools.get(name)
    
    def profile(self) -> PerfProfiler:
        return self._profiler
    
    def intern_string(self, s: str) -> str:
        return self._string_intern.intern(s)
    
    def track_hot_path(self, func_name: str) -> tuple[bool, float]:
        return self._hot_path.track(func_name)
    
    def stats(self) -> dict[str, Any]:
        return {
            "caches": {name: cache.stats() for name, cache in self._caches.items()},
            "pools": {name: pool.stats() for name, pool in self._pools.items()},
            "profiler": self._profiler.stats(),
            "hot_paths": self._hot_path.stats(),
        }


def New() -> PerformanceOptimizerPlugin:
    return PerformanceOptimizerPlugin()
