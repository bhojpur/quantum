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

#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/complex.h>
#include <pybind11/stl.h>
#include <pybind11/pytypes.h>
#include <vector>
#include <complex>
#include <iostream>
#if defined(_OPENMP)
#include <omp.h>
#endif
#include "_cppkernels/simulator.hpp"

namespace py = pybind11;

using c_type = std::complex<double>;
using ArrayType = std::vector<c_type, aligned_allocator<c_type,64>>;
using MatrixType = std::vector<ArrayType>;
using QuRegs = std::vector<std::vector<unsigned>>;

template <class QR>
void emulate_math_wrapper(Simulator &sim, py::function const& pyfunc, QR const& qr, std::vector<unsigned> const& ctrls){
    auto f = [&](std::vector<int>& x) {
        pybind11::gil_scoped_acquire acquire;
        x = pyfunc(x).cast<std::vector<int>>();
    };
    pybind11::gil_scoped_release release;
    sim.emulate_math(f, qr, ctrls);
}

PYBIND11_MODULE(_cppsim, m)
{
    py::class_<Simulator>(m, "Simulator")
        .def(py::init<unsigned>())
        .def("allocate_qubit", &Simulator::allocate_qubit)
        .def("deallocate_qubit", &Simulator::deallocate_qubit)
        .def("get_classical_value", &Simulator::get_classical_value)
        .def("is_classical", &Simulator::is_classical)
        .def("measure_qubits", &Simulator::measure_qubits_return)
        .def("apply_controlled_gate", &Simulator::apply_controlled_gate<MatrixType>)
        .def("emulate_math", &emulate_math_wrapper<QuRegs>)
        .def("emulate_math_addConstant", &Simulator::emulate_math_addConstant<QuRegs>)
        .def("emulate_math_addConstantModN", &Simulator::emulate_math_addConstantModN<QuRegs>)
        .def("emulate_math_multiplyByConstantModN", &Simulator::emulate_math_multiplyByConstantModN<QuRegs>)
        .def("get_expectation_value", &Simulator::get_expectation_value)
        .def("apply_qubit_operator", &Simulator::apply_qubit_operator)
        .def("emulate_time_evolution", &Simulator::emulate_time_evolution)
        .def("get_probability", &Simulator::get_probability)
        .def("get_amplitude", &Simulator::get_amplitude)
        .def("set_wavefunction", &Simulator::set_wavefunction)
        .def("collapse_wavefunction", &Simulator::collapse_wavefunction)
        .def("run", &Simulator::run)
        .def("cheat", &Simulator::cheat)
        ;
}