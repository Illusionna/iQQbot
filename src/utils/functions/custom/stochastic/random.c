/*
macOS Sonoma Apple clang version 15.0.0 (clang-1500.3.9.4)
Target: arm64-apple-darwin23.6.0

>>> gcc -shared -o random.dll random.c
*/

# include <math.h>
# include <time.h>
# include <stdio.h>
# include <stdlib.h>


static unsigned long long seed = 1;

// 初始化随机种子.
void Srand48(unsigned int i) {
    seed = (((long long int)i) << 16) | rand();
}

// 生成 [0, 1] 之间均匀分布的伪随机数.
double Drand48(void) {
    seed = (0x5DEECE66DLL * seed + 0xB16) & 0xFFFFFFFFFFFFLL;
    unsigned int x = seed >> 16;
    return ((double)x / (double)0x100000000LL);
}

// 生成 [a, b] 之间均匀分布随机数.
double GenerateRandom(double a, double b) {
    return a + (b - a) * Drand48();
}