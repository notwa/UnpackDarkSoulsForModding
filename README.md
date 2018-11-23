# UnpackDarkSoulsForModding

Unpacks Dark Souls 1 archive files.
This fork has been modified to work with the files from the
PlayStation 3 release of the game.

Instructions:

Before beginning, make sure you have at least 10GB of free hard-disk space and 1GB of available RAM.

The `unpack_dark_souls_for_modding.py` interface is currently broken.
You should instead do the following:

* Find and extract the `dvdbnd.bdt` and `dvdbnd.bhd5` files from your game disk.

* `cd` into the directory where you extracted those files.

* run `python2 /path/to/UnpackDarkSoulsForModding/unpacker_file_handler.py`

* Files are unpacked into subdirectories. Enjoy!

Note that this fork also lacks ability to modify
the game executable to load the unpacked files.
I do not have a way of doing nor testing this at this time.
