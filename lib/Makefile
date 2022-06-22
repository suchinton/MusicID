all: libmusicID.so musicID genperm

SOURCES=wav.c fingerprinting.c fft.c logbins.c spectralimages.c haar.c rawfingerprints.c minhash.c permutations.c fingerprintio.c \
        resample.c audionormalizer.c hannwindow.c search.c ffmpeg.c lsh.c

musicID: main.c libmusicID.so
	$(CC) -L. main.c -lmusicID -lm -Wl,-rpath,. -o musicID -Wall -Wextra -pedantic

libmusicID.so: $(SOURCES)
	$(CC) -fPIC $(SOURCES) -lpthread -shared -o libmusicID.so -Wall -Wextra -pedantic

genperm: generatepermutations.c
	$(CC) generatepermutations.c -o genperm -Wall -Wextra -pedantic

clean:
	rm -f musicID libmusicID.so
