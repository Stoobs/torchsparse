#include "hashmap_cpu.hpp"

#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <stdexcept>

#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable: 4244) // conversion warnings
#pragma warning(disable: 4267) // conversion warnings
#endif

void HashTableCPU::lookup_vals(const int64_t* const keys,
                             int64_t* const results, const int n) {
#ifdef _MSC_VER
    for (int idx = 0; idx < n; idx++) {
#else
#pragma omp parallel for
    for (int idx = 0; idx < n; idx++) {
#endif
        int64_t key = keys[idx];
        auto iter = hashmap.find(key);
        if (iter != hashmap.end()) {
            results[idx] = iter->second;
        } else {
            results[idx] = 0;
        }
    }
}

void HashTableCPU::insert_vals(const int64_t* const keys,
                             const int64_t* const vals, const int n) {
    for (int i = 0; i < n; i++) {
        hashmap[keys[i]] = vals[i];
    }
}

#ifdef _MSC_VER
#pragma warning(pop)
#endif
