---
release type: minor
---

Renamed package from `lia-web` to `cross-web`. The import name is now `cross_web`.

```python
from cross_web import Response
```

If you were using `lia-web`, you can continue using it as a compatibility shim - it now depends on `cross-web` and re-exports all symbols. However, we recommend updating your imports to use `cross_web` directly.
