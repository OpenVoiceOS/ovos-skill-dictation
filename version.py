# START_VERSION_BLOCK
VERSION_MAJOR = 0
VERSION_MINOR = 3
VERSION_BUILD = 0
VERSION_ALPHA = 1
# END_VERSION_BLOCK

# derived for setuptools dynamic version (do not edit the block above)
if int(VERSION_ALPHA):
    __version__ = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}a{VERSION_ALPHA}"
else:
    __version__ = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
