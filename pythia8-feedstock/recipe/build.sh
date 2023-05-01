#!/usr/bin/env bash
set -e

if [[ "${target_platform}" == linux-* ]]; then
    PYTHIA_ARCH=LINUX
else
    PYTHIA_ARCH=DARWIN
fi

EXTRAS=""

# Use pybind11 from conda-forge
sed -i 's@overload_caster_t@override_caster_t@g' plugins/python/src/*.cpp
rm -rf plugins/python/include/pybind11
ln -s $PREFIX/include/pybind11 $PWD/plugins/python/include/pybind11

# Copy plugin needed for FxFx
cp "${RECIPE_DIR}/JetMatching.h" "${PWD}/include/Pythia8Plugins/JetMatching.h"

./configure \
    --with-python-include="$(python -c "from sysconfig import get_paths; info = get_paths(); print(info['include'])")" \
    --with-python-bin="${PREFIX}/bin/" \
    --arch=${PYTHIA_ARCH} \
    --prefix=${PREFIX} \
    --with-hepmc2=${PREFIX} \
    --with-gzip=${PREFIX} \
    --with-lhapdf6 \
    --with-lhapdf6-plugin=LHAPDF6.h \
    --cxx-common='-ldl -fPIC -lstdc++ -std=c++11 -pthread -O2 -DHEPMC2HACK'
    ${EXTRAS}

make install -j${CPU_COUNT}

# Make links so conda can find the bindings
ln -s "${PREFIX}/lib/pythia8.so" "${SP_DIR}/"
