# circuit-breaker 熔断器

为插件提供熔断能力，防止级联失败。

## 功能

- 失败计数熔断
- 状态：`closed` → `open` → `half-open`
- 可配置失败阈值
- 自动恢复机制

## 状态机

```
closed (正常) → open (熔断) → half-open (半开) → closed (恢复)
```

## 使用

```python
# 检查是否有熔断能力
if "circuit_breaker" in capabilities:
    breaker = extensions["_circuit_breaker_provider"]
    cb = breaker.create("my-plugin", threshold=5)
    
    try:
        result = cb.call(risky_function, arg1, arg2)
    except Exception:
        print("熔断器已触发")
```
