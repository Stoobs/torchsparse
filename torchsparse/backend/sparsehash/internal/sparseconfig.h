#ifndef SPARSEHASH_INTERNAL_SPARSECONFIG_H_
#define SPARSEHASH_INTERNAL_SPARSECONFIG_H_

// --- Basic platform detection ---
#if defined(_MSC_VER)
  #define SPARSEHASH_WINDOWS 1
#endif

// --- Namespace definition ---
// Used by densehashtable.h and sparsehashtable.h
#if defined(SPARSEHASH_WINDOWS)
  #define GOOGLE_NAMESPACE  ::google
  #define _START_GOOGLE_NAMESPACE_  namespace google {
  #define _END_GOOGLE_NAMESPACE_    }
#else
  // Default for other platforms
  #define GOOGLE_NAMESPACE  ::google
  #define _START_GOOGLE_NAMESPACE_  namespace google {
  #define _END_GOOGLE_NAMESPACE_    }
#endif

// --- System-specific includes and type definitions ---
#if defined(SPARSEHASH_WINDOWS)
  #include <stdlib.h>  // For abort(), getenv()
  #include <stddef.h>  // For ptrdiff_t
  #if (_MSC_VER >= 1600) // VS 2010 and later (which windows-2022 runner uses)
    #include <stdint.h>  // Defines intN_t, uintN_t, etc.
  #else
    // Fallback for very old MSVC, not strictly needed for VS2019/2022
    typedef signed __int8 int8_t;
    typedef signed __int16 int16_t;
    typedef signed __int32 int32_t;
    typedef signed __int64 int64_t;
    typedef unsigned __int8 uint8_t;
    typedef unsigned __int16 uint16_t;
    typedef unsigned __int32 uint32_t;
    typedef unsigned __int64 uint64_t;
  #endif
  #define HAVE_UINT16_T 1
  #define HAVE_U_INT16_T 1 // Common alias for uint16_t availability
  #define HAVE_LONG_LONG 1 // MSVC supports long long
  #define HAVE_STDINT_H 1  // We are including stdint.h
  // #define HAVE_INTTYPES_H 0 // Not typically needed with stdint.h on MSVC
  // #define HAVE_SYS_TYPES_H 0 // Not a standard MSVC header
#else
  // For non-Windows (Linux, macOS)
  #include <stdint.h>
  #include <sys/types.h>
  #include <stddef.h>
  #define HAVE_UINT16_T 1
  #define HAVE_U_INT16_T 1
  #define HAVE_LONG_LONG 1
  #define HAVE_STDINT_H 1
#endif

// Define if you have the tr1 unordered_map header (not usually needed for sparsehash's own types)
// #define HAVE_TR1_UNORDERED_MAP 0
// #define HAVE_TR1_UNORDERED_SET 0

// Define if you have the C++11 unordered_map header (not usually needed for sparsehash's own types)
// #define HAVE_CXX11_UNORDERED_MAP 0
// #define HAVE_CXX11_UNORDERED_SET 0

#endif  // SPARSEHASH_INTERNAL_SPARSECONFIG_H_