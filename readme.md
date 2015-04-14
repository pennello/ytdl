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
Simply run `make && sudo make install`.  The `Makefile` takes advantage
of GNU extensions; therefore, you will want to use `gmake` on FreeBSD.
The `Makefile` supports `DESTDIR`.

Running
-------
Run `ytdl`.

Files
-----
 - `/usr/local/bin/ytdl` (via `make install`)
 - `$HOME/etc/ytdl.conf`
 - `$HOME/var/db/ytdl/*` (created at runtime)
 - `$HOME/var/log/ytdl/cron_dlsubs.log` (created by `cron dlsubs`)

Future Work
-----------
- Write man page.
- Write extensive Pydoc documentation.
- Write goals/background documentation.
- Don't require config for `clip listen`.
