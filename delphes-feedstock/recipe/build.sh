#!/usr/bin/env bash
set -e

PYTHIA8=${PREFIX}
make HAS_PYTHIA8=true

# Install libraries
cp -fp libDelphes.so libDelphesNoFastJet.so "${PREFIX}/lib"
cp -fp ClassesDict_rdict.pcm ExRootAnalysisDict_rdict.pcm FastJetDict_rdict.pcm ModulesDict_rdict.pcm Pythia8Dict_rdict.pcm "${PREFIX}/lib"
ln -s ../lib/ClassesDict_rdict.pcm ../lib/ExRootAnalysisDict_rdict.pcm ../lib/FastJetDict_rdict.pcm ../lib/ModulesDict_rdict.pcm ../lib/Pythia8Dict_rdict.pcm "${PREFIX}/bin"

# Install executables
cp -fp CaloGrid DelphesHepMC2 DelphesHepMC3 DelphesLHEF DelphesPythia8 DelphesROOT DelphesSTDHEP hepmc2pileup lhco2root pileup2root root2lhco root2pileup stdhep2pileup "${PREFIX}/bin"
ln -s DelphesHepMC2 "${PREFIX}/bin/DelphesHepMC"

# Install include files
mkdir -p "${PREFIX}/include/classes" "${PREFIX}/include/modules"
cp -fp classes/*.h "${PREFIX}/include/classes"
cp -fp modules/*.h "${PREFIX}/include/modules"
cp -fpR external/ExRootAnalysis external/Hector external/PUPPI external/TrackCovariance external/fastjet external/tcl "${PREFIX}/include"

# Install share files
mkdir "${PREFIX}/share/delphes"
cp -fpR cards doc examples validation "${PREFIX}/share/delphes"
