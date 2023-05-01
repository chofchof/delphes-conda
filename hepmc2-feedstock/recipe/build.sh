#!/usr/bin/env bash
# Enable bash strict mode
# http://redsymbol.net/articles/unofficial-bash-strict-mode/
set -euo pipefail
IFS=$'\n\t'

# Copying the hacked files 'WeightContainer.cc' and 'WeightContainer.h' to be capable of writing named weights in HepMC.

mkdir -p build
cd build

cmake -LAH \
    -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_INSTALL_PREFIX=${PREFIX} \
    -Dmomentum:STRING=GEV -Dlength:STRING=MM \
    ../source 


make -j${CPU_COUNT}

if [ "$(uname)" == "Linux" ]; then
make test
fi

make install
exit 0
