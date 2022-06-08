// Copyright (c) 2018 Bhojpur Consulting Private Limited, India. All rights reserved.

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in
// all copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
// THE SOFTWARE.

#pragma once

#ifdef _WIN32
#include <malloc.h>
#else
#include <cstdlib>
#endif
#include <cstddef>
#include <memory>
#include <new>

#if __cplusplus < 201103L
#define noexcept
#endif

template <typename T, unsigned int Alignment>
class aligned_allocator
{
 public:
    typedef T* pointer;
    typedef T const* const_pointer;
    typedef T& reference;
    typedef T const& const_reference;
    typedef T value_type;
    typedef std::size_t size_type;
    typedef std::ptrdiff_t difference_type;

    template <typename U>
    struct rebind
    {
        typedef aligned_allocator<U, Alignment> other;
    };

    aligned_allocator() noexcept {}
    aligned_allocator(aligned_allocator const&) noexcept {}
    template <typename U>
    aligned_allocator(aligned_allocator<U, Alignment> const&) noexcept
    {
    }

    pointer allocate(size_type n)
    {
        pointer p;


#ifdef _WIN32
        p = reinterpret_cast<pointer>(_aligned_malloc(n * sizeof(T), Alignment));
        if (p == 0) throw std::bad_alloc();
#else
        if (posix_memalign(reinterpret_cast<void**>(&p), Alignment, n * sizeof(T)))
            throw std::bad_alloc();
#endif
        return p;
    }

    void deallocate(pointer p, size_type) noexcept
    {
#ifdef _WIN32
        _aligned_free(p);
#else
        std::free(p);
#endif
    }

    size_type max_size() const noexcept
    {
        std::allocator<T> a;
        return a.max_size();
    }

#if __cplusplus >= 201103L
    template <typename C, class... Args>
    void construct(C* c, Args&&... args)
    {
        new ((void*)c) C(std::forward<Args>(args)...);
    }
#else
    void construct(pointer p, const_reference t) { new ((void*)p) T(t); }
#endif

    template <typename C>
    void destroy(C* c)
    {
        c->~C();
    }

    bool operator==(aligned_allocator const&) const noexcept { return true; }
    bool operator!=(aligned_allocator const&) const noexcept { return false; }
    template <typename U, unsigned int UAlignment>
    bool operator==(aligned_allocator<U, UAlignment> const&) const noexcept
    {
        return false;
    }

    template <typename U, unsigned int UAlignment>
    bool operator!=(aligned_allocator<U, UAlignment> const&) const noexcept
    {
        return true;
    }
};

#if __cplusplus < 201103L
#undef noexcept
#endif