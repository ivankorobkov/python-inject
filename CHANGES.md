python-inject changes
=====================

### 3.5.0 (2019-03-11)
- Configurable auto-initialization, #23
  [@Fedorof](https://github.com/Fedorof).

### 3.4.0 (2018-08-01)
- Type hinting in Python 3, #20
  [@Enforcer](https://github.com/Enforcer).
- Autoparams leveraging types annotations, #21
  [@Enforcer](https://github.com/Enforcer).

### 3.3.2 (2017-09-14)
- Use getfullargspec when executing in Python3, #17
  [@jaimewyant](https://github.com/jaimewyant).

### 3.3.1 (2015-03-28)
- Fixed race condition in bind_to_constructor, #14
  [@peick](https://github.com/peick).

### 3.3.0 (2014-08-22)
- Added `inject.params(arg1=cls1, arg2=cls2)`, deprecated `inject.param`, #12
  (thanks [@scharf](https://github.com/scharf)).

### 3.2.0 (2014-08-04)
- Added `inject.configure_once` and `inject.is_configured`, #11. 

### 3.1.1 (2014-03-14)
- Switch from root logger to module logger, #8.

### 3.1.0 (2014-03-07)
- `inject.param` decorator.
- Small fixes in exceptions.

### 3.0.0 (2014-02-10)
- Smaller, better, faster version with simpler and cleaner API.
 
### 2.0.0-alpha1 (2010-08-25)
- Second version (never made it to stable).

### 1.0.0 (2010-02-12)
- Initial release.
