python-inject changes
=====================

### 5.1.0 (2023-10-17)
- Optionally allow overriding dependencies.
- Unified configure syntax with clear and once flags.

### 5.0.0 (2023-06-10)
- Support for PEP0604 for Python>=3.10.

### 4.3.1 (2020-08-17)
- Use assertRaisesRegex instead of assertRaisesRegexp to fix deprecation warnings.

### 4.3.0 (2020-08-11)
- Support for classes in autoparams, #59.
- Support for asyncio, #66.

### 4.2.0 (2020-05-15)
- Migrated autoparams and annotations to typing.get_type_hints.
- Fix boolean casting to make possible to inject DataFrame (#55) #56.
- Add support for forward references #54.

### 4.1.2 (2020-04-13)
- Include py.typed and manifest in dist, #50.

### 4.1.1 (2020-02-25)
- UTF8 encoding for readme in setup.py, #48.

### 4.1.0 (2020-02-24)
- More precise typing #47.
- Removed Python 3.5 support.

### 4.0.0 (2019-11-25)
- Drop Python <3.5 support.
- [feature] Add typed information, #43.
- [chore] Remov old typing information as it is no longer relevant for v4.0.0, #43.

### 3.5.4 (2019-07-30)
- MyPy compatibility #36.

### 3.5.3 (2019-07-24)
- AttributeError: type object 'Callable' has no attribute '_abc_registry' #34

### 3.5.2 (2019-07-10)
- Modify type-hints to support Hashable bindings and other improvements,  #33.
- Merge these type-hints into the .py file instead of having a .pyi file, #33.

### 3.5.1 (2019-04-16)
- Export Binder and Injector in pyi, #29.
- Make autoparams work with keyword-only parameters, #26.

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
