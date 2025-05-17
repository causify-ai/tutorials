#!/bin/csh
setenv TBBROOT "/project/python/build/lib.linux-x86_64-cpython-39/prophet/stan_model/cmdstan-2.33.1/stan/lib/stan_math/lib/tbb_2020.3" #
setenv tbb_bin "/project/python/build/lib.linux-x86_64-cpython-39/prophet/stan_model/cmdstan-2.33.1/stan/lib/stan_math/lib/tbb" #
if (! $?CPATH) then #
    setenv CPATH "${TBBROOT}/include" #
else #
    setenv CPATH "${TBBROOT}/include:$CPATH" #
endif #
if (! $?LIBRARY_PATH) then #
    setenv LIBRARY_PATH "${tbb_bin}" #
else #
    setenv LIBRARY_PATH "${tbb_bin}:$LIBRARY_PATH" #
endif #
if (! $?LD_LIBRARY_PATH) then #
    setenv LD_LIBRARY_PATH "${tbb_bin}" #
else #
    setenv LD_LIBRARY_PATH "${tbb_bin}:$LD_LIBRARY_PATH" #
endif #
 #
