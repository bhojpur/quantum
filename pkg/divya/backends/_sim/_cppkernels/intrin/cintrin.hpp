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

#ifndef CINTRIN_HPP_
#define CINTRIN_HPP_

#include <immintrin.h>
#include <complex>

#ifndef _mm256_set_m128d
#define _mm256_set_m128d(hi,lo) _mm256_insertf128_pd(_mm256_castpd128_pd256(lo), (hi), 0x1)
#endif
#ifndef _mm256_storeu2_m128d
#define _mm256_storeu2_m128d(hiaddr,loaddr,a) do { __m256d _a = (a); _mm_storeu_pd((loaddr), _mm256_castpd256_pd128(_a)); _mm_storeu_pd((hiaddr), _mm256_extractf128_pd(_a, 0x1)); } while (0)
#endif
#ifndef _mm256_loadu2_m128d
#define _mm256_loadu2_m128d(hiaddr,loaddr) _mm256_set_m128d(_mm_loadu_pd(hiaddr), _mm_loadu_pd(loaddr))
#endif

template <class T>
class cintrin;

template <>
class cintrin<double>{
public:
    using calc_t = double;
    using ret_t = cintrin<calc_t>;


    cintrin() {}

    template <class U>
    cintrin(U const *p){
        v_ = _mm256_load_pd((calc_t const*)p);
    }

    template <class U>
    cintrin(U const *p1, U const *p2){
        v_ = _mm256_loadu2_m128d((calc_t const*)p2, (calc_t const*)p1);
    }

    template <class U>
    cintrin(U const *p, bool broadcast){
        auto tmp = _mm_load_pd((calc_t const*)p);
        v_ = _mm256_broadcast_pd(&tmp);
    }

    explicit cintrin(calc_t const& s1){
        v_ = _mm256_set1_pd(s1);
    }

    cintrin(__m256d const& v) : v_(v) {  }

    std::complex<calc_t> operator[](unsigned i){
        calc_t v[4];
        _mm256_store_pd(v, v_);
        return {v[i*2], v[i*2+1]};
    }

    template <class U>
    void store(U *p) const{
        _mm256_store_pd((calc_t *)p, v_);
    }

    template <class U>
    void store(U *p1, U *p2) const{
        _mm256_storeu2_m128d((calc_t *)p2, (calc_t *)p1, v_);
    }
    __m256d v_;
};

inline cintrin<double> mul(cintrin<double> const& c1, cintrin<double> const& c2, cintrin<double> const& c2tm){
    auto ac_bd = _mm256_mul_pd(c1.v_, c2.v_);
    auto multbmadmc = _mm256_mul_pd(c1.v_, c2tm.v_);
    return cintrin<double>(_mm256_hsub_pd(ac_bd, multbmadmc));
}
inline cintrin<double> operator*(cintrin<double> const& c1, cintrin<double> const& c2){
    __m256d neg = _mm256_setr_pd(1.0, -1.0, 1.0, -1.0);
    auto badc = _mm256_permute_pd(c2.v_, 5);
    auto bmadmc = _mm256_mul_pd(badc, neg);
    return mul(c1, c2, bmadmc);
}
inline cintrin<double> operator+(cintrin<double> const& c1, cintrin<double> const& c2){
    return cintrin<double>(_mm256_add_pd(c1.v_, c2.v_));
}
inline cintrin<double> operator*(cintrin<double> const& c1, double const& d){
    auto d_d = _mm256_set1_pd(d);
    return _mm256_mul_pd(c1.v_, d_d);
}
inline cintrin<double> operator*(double const& d, cintrin<double> const& c1){
    return c1*d;
}



inline __m256d mul(__m256d const& c1, __m256d const& c2, __m256d const& c2tm){
    auto ac_bd = _mm256_mul_pd(c1, c2);
    auto multbmadmc = _mm256_mul_pd(c1, c2tm);
    return _mm256_hsub_pd(ac_bd, multbmadmc);
}
inline __m256d add(__m256d const& c1, __m256d const& c2){
    return _mm256_add_pd(c1, c2);
}
template <class U>
inline __m256d load2(U *p){
    auto tmp = _mm_load_pd((double const*)p);
    return _mm256_broadcast_pd(&tmp);
}
template <class U>
inline __m256d load(U const*p1, U const*p2){
    return _mm256_loadu2_m128d((double const*)p2, (double const*)p1);
}
#endif