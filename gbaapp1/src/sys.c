/* Freestanding libc stubs */
#include "gba.h"

void *memset(void *s, int c, unsigned n)
{
	u8 *p = (u8 *)s;
	while (n--)
		*p++ = (u8)c;
	return s;
}

void *memcpy(void *dst, const void *src, unsigned n)
{
	u8 *d = (u8 *)dst;
	const u8 *s = (const u8 *)src;
	while (n--)
		*d++ = *s++;
	return dst;
}

void *memmove(void *dst, const void *src, unsigned n)
{
	u8 *d = (u8 *)dst;
	const u8 *s = (const u8 *)src;
	if (d < s) {
		while (n--)
			*d++ = *s++;
	} else {
		d += n;
		s += n;
		while (n--)
			*--d = *--s;
	}
	return dst;
}

int memcmp(const void *a, const void *b, unsigned n)
{
	const u8 *p = (const u8 *)a;
	const u8 *q = (const u8 *)b;
	while (n--) {
		if (*p != *q)
			return *p - *q;
		p++;
		q++;
	}
	return 0;
}

void __aeabi_memcpy(void *dst, const void *src, unsigned n) { memcpy(dst, src, n); }
void __aeabi_memcpy4(void *dst, const void *src, unsigned n) { memcpy(dst, src, n); }
void __aeabi_memcpy8(void *dst, const void *src, unsigned n) { memcpy(dst, src, n); }
void __aeabi_memclr(void *dst, unsigned n) { memset(dst, 0, n); }
void __aeabi_memclr4(void *dst, unsigned n) { memset(dst, 0, n); }
void __aeabi_memclr8(void *dst, unsigned n) { memset(dst, 0, n); }
void __aeabi_memset(void *dst, unsigned n, int c) { memset(dst, c, n); }
