Setup
-----
Place a file `ytdl.conf` in `$HOME/etc`.  Its contents should look
something like the following.

    [auth]
    key = AIzaSyAujM2qD38VDMpfQHXQv3XjJx-Mjzb5Xs4

The key should be an application server key, created on the [Google
developers console](https://console.developers.google.com/).  It will be
used when making calls to the YouTube Data API (v3).

Installation
------------
Run `sh install.sh`.  It will symlink `ytdl` into `$HOME/bin`.

Running
-------
Run `ytdl`.  It's a wrapper for the Python code in the `ytdl` package
which is inside the `lib` directory.

Files
-----
 - `$HOME/bin/ytdl` (via `install.sh`)
 - `$HOME/etc/ytdl.conf`
 - `$HOME/var/db/ytdl/*` (created at runtime)
 - `$HOME/var/log/ytdl/cron_dlsubs.log` (created by `cron dlsubs`)

Future Work
-----------
Write man page.
Write extensive Pydoc documentation.
Write goals/background documentation.
