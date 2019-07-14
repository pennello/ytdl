# chris 041315

.PHONY: install uninstall clean

DESTDIR = /usr/local

name = ytdl
bin = $(name)
zip = $(name).zip
pyo = $(patsubst %.py, %.pyo, $(shell find src -name '*.py'))

$(bin): src/header $(zip)
	cat $^ > $@
	chmod +x $@

$(zip): $(pyo)
	rm -f $@
	cd src && echo $(patsubst src/%, %, $^) | xargs zip -9 ../$@

%.pyo: %.py
	python2 -OOm py_compile $^

clean:
	rm -f $(bin) $(zip) $(pyo)

install:
	install $(bin) $(DESTDIR)/bin/$(bin)

uninstall:
	rm $(DESTDIR)/bin/$(bin)
