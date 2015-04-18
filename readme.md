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
subscriptions directly in the same manner as channel subscriptions.

`ytdl` supports two main use cases.

1. Download your latest subscriptions.
2. Wach the clipboard for YouTube URLs, and download them automatically.

Dependencies
------------
`ytdl` makes use of the excellent program [`youtube-dl`][3] to do the
actual heavy lifting of downloading YouTube videos.  It's launched as a
subprocess, and needs to be in your path.

Installation
------------
Simply run `make && sudo make install`.  The `Makefile` takes advantage
of GNU extensions; therefore, you will want to use `gmake` on FreeBSD.
The `Makefile` supports `DESTDIR`.

Latest Subscription Download
----------------------------
The first use case is to download the most-recent unseen uploads to a
specified directory.  Ideal for `cron`.

Place a file `ytdl.conf` in `$HOME/etc`.  Its contents should look
something like the following.

    [auth]
    key = AIzaSyAujM2qD38VDMpfQHXQv3XjJx-Mjzb5Xs4

The key should be an application server key, created on the [Google
developers console][2].  It will be used when making calls to the
YouTube Data API (v3).

Next, import your current YouTube subscriptions.  First, if you don't
have it, get the channel ID for your user.

    ytdl id get <yourusername>

Then, import the subscriptions for that channel ID.

    ytdl subs import <channelid>

Just the IDs of the channels to which this channel is subscribed will be
imported.  Now you can run the following command to fetch and download
the latest subscriptions that you haven't yet seen.

    ytdl cron dlsubs -s <where/to/save/the/videos>

Note that in the first run through, `ytdl` will not actually download
anything.  Instead, it will store the most-recent video IDs in each
channel.  Future invocations will continue to update this "seen state",
so `ytdl` won't download the same videos multiple times.

Clipboard Listening
-------------------
The second use case is to watch the clipboard for YouTube video URLs,
and automatically download them to the current working directory.  No
API key required; simply run the following.

    ytdl clip listen

Documentation
-------------
`ytdl` has a number of commands.  In fact, the commands themselves are
subdivided into command groups, wich commands underneath each group.
All levels of invocation are well-documented with support for a `--help`
option.  Run `ytdl --help` to get started.

In addition, most of the classes and methods have Pydoc documentation.

Files
-----
 - `/usr/local/bin/ytdl` (via `make install`)
 - `$HOME/etc/ytdl.conf`
 - `$HOME/var/db/ytdl/*` (created at runtime)
 - `$HOME/var/log/ytdl/cron_dlsubs.log` (created by `cron dlsubs`)

[1]: http://youtube-eng.blogspot.com/2015/03/dude-are-you-still-on-youtube-api-v2.html
[2]: https://console.developers.google.com/
[3]: http://rg3.github.io/youtube-dl/
