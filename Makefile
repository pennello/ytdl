# chris 041315

.PHONY: install uninstall clean

DESTDIR = /usr/local

name = ytdl
bin = $(name)
zip = $(name).zip
pyc = $(patsubst %.py, %.pyc, $(shell find src -name '*.py'))

$(bin): src/header $(zip)
	cat $^ > $@
	chmod +x $@

$(zip): $(pyc)
	rm -f $@
	cd src && echo $(patsubst src/%, %, $^) | xargs zip -9 ../$@

%.pyc: %.py
	python3 -OO compile.py $^

clean:
	rm -f $(bin) $(zip) $(pyc)

install:
	install $(bin) $(DESTDIR)/bin/$(bin)

uninstall:
	rm $(DESTDIR)/bin/$(bin)
