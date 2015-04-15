Goals & Background
------------------
[YouTube no longer offers version 2 of their API][1], which included 
feeds for the uploads of channels to which you were subscribed.  In
addition, this API version also provided feeds for individual playlists,
which was very useful for the case in which you were interested in
watching new videos on a particular topic, but not for the channel in
general.  In addition, YouTube has an incentive to subtly modify the
content returned in your home feed.

`ytdl` replaces your YouTube subscription management.  You no longer
manage your YouTube channel subscriptions on youtube.com, and instead
manage them through this tool.  In addition, you can manage playlist
subscriptions as well.

`ytdl` supports two main use cases.

1. Download the most-recent unseen uploads to a specified directory.
   Ideal for `cron`.
2. Watch the clipboard for YouTube video URLs, and automatically
   download them.

Setup
-----
Place a file `ytdl.conf` in `$HOME/etc`.  Its contents should look
something like the following.

    [auth]
    key = AIzaSyAujM2qD38VDMpfQHXQv3XjJx-Mjzb5Xs4

The key should be an application server key, created on the [Google
developers console][2].  It will be used when making calls to the
YouTube Data API (v3).

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
- Don't require config for `clip listen`.

References
----------
[1]: http://youtube-eng.blogspot.com/2015/03/dude-are-you-still-on-youtube-api-v2.html
[2]: https://console.developers.google.com/
