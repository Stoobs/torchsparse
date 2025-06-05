#pragma once

#include <cmath>
#include <cstdint>
#include <cstdio>
#include <cstdlib>
#include <vector>

#ifdef _MSC_VER
#pragma warning(push)
#pragma warning(disable: 4244) // conversion warnings
#pragma warning(disable: 4267) // conversion warnings
#include <sparsehash/internal/sparseconfig.h>
#endif
#include <sparsehash/dense_hash_map>

class HashTableCPU {
 private:
  google::dense_hash_map<int64_t, int64_t> hashmap;

 public:
  HashTableCPU() {
    hashmap.set_empty_key(-1);  // Required for dense_hash_map
  }

  ~HashTableCPU() {}

  void insert_vals(const int64_t* const keys, const int64_t* const vals,
                   const int n);

  void lookup_vals(const int64_t* const keys, int64_t* const results,
                   const int n);
};

#ifdef _MSC_VER
#pragma warning(pop)
#endif
