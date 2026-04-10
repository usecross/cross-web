---
release type: minor
---

Add `cross_web.testing.clients`, a shared request-integration client matrix
for the supported frameworks.

This moves the reusable request test harnesses out of `tests/` and into a
package that other projects can import directly, including the Django test
URLConf needed by the client suite.
