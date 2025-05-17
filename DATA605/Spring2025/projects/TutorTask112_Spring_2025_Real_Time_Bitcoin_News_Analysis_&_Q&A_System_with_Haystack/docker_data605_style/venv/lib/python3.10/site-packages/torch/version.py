from typing import Optional

__all__ = ['__version__', 'debug', 'cuda', 'git_version', 'hip']
__version__ = '2.7.0'
debug = False
cuda: Optional[str] = None
git_version = '134179474539648ba7dee1317959529fbd0e7f89'
hip: Optional[str] = None
xpu: Optional[str] = None
