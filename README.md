CCleaner Auto Update
==================
[![license][license-img]][github] [![github][github-img]][github]

Automatic updater of [CCleaner (Crap Cleaner)][ccleaner], awesome PC Optimizor for Windows PCs.

Free version of CCleaner does not support automatic update, and only notifies it, so every time there is an update you have to visit official homepage, download it, and install it. This script does it in a row.

## Before you start
Please consider buy CCleaner(https://www.piriform.com/ccleaner/download) if you like it.

## How to use
There are ready packages for the latest [releases][release].
If there's no build suit to you, please see [Build][] section to make you own OR it's just fine to use raw Python script.

Inside of package, you must have to check config.cfg file with following instruction.

* **ccleaner_path**: Put correct install path to CCleaner. If you didn't make any special modification, default is `C:\\Program Files\\CCleaner\\CCleaner.exe`
* **release_url**: (optional) Web page url to release note to capture new version.
* **release_re**: (optional) Regx to capture release version.
* **download_url**: (optional) Web page url to capture download link.
* **download_re**: (optional) Regx to capture download link.
* **install_arg**:	Installer arguments. Please pick your preferred language from http://support.microsoft.com/kb/221435 and replace `1042`(Currnetly set to Korean) with your locale code. You can optionally set installer arguments like `/S`(Silent install)
* **keep_file**: (optional) Option to keep downloaded CCleaner installer. `pre` to keep only latest installer, `post` to preserve nothing. Default is `none` which will keep preserve every downloaded releases.

## Build
To build executive binary yourself from Python script, you need [py2exe](http://www.py2exe.org/) package. First install proper py2exe package from link.

Then clone this project with [`git`][git]:

~~~
> git clone git@github.com:bskim45/ccleanerautoupdate.git
> cd ccleanerautoupdate
~~~

Also you can download it as [zip (master)](https://github.com/bskim45/ccleanerautoupdate/archive/master.zip)

and run the following command to build:

~~~
> python to_binary_compressed.py py2exe
~~~

If it worked properly, two folders `build`, `dist` will be created. You can find your executive inside of `dist`.


## License

The MIT License (MIT)

Copyright (c) 2015 Bumsoo Kim (http://bsk.im)

see [LICENSE](https://github.com/bskim45/ccleanerautoupdate/blob/master/LICENSE) for details.

[ccleaner]: https://www.piriform.com/ccleaner
[github]: https://github.com/bskim45/ccleanerautoupdate
[github-issues]: https://github.com/lbskim45/ccleanerautoupdate/issues
[github-release]: https://github.com/bskim45/ccleanerautoupdate/releases
[git]: http://git-scm.com

[release-img]: https://img.shields.io/badge/release-0.2-green.svg?style=flat-square
[license-img]: https://img.shields.io/badge/license-MIT-blue.svg?style=flat-square
[github-img]: https://img.shields.io/badge/github-bskim45/ccleanerautoupdate-yellowgreen.svg?style=flat-square