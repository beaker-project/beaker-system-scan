
HELPER_PROGRAMS = getdriver.sh
BUILT_FILES =
ifeq ($(shell arch),x86_64)
    HELPER_PROGRAMS += hvm_detect
    BUILT_FILES += hvm_detect
endif

.PHONY: all
all: $(BUILT_FILES)

hvm_detect: hvm_detect.c
	gcc $(CFLAGS) -o $@ $^

.PHONY: install
install: $(BUILT_FILES)
	python setup.py install -O1 --root $(DESTDIR)
	mkdir -p $(DESTDIR)/usr/libexec/beaker-system-scan/
	cp -p $(HELPER_PROGRAMS) $(DESTDIR)/usr/libexec/beaker-system-scan/
