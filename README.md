# Delphes for Conda
Delphes, Pythia8, and HepMC2 packages for [conda](https://conda.io) to work with [MadGraph5_aMC@NLO](https://launchpad.net/mg5amcnlo).

- **Delphes 3.5.0**: A framework for fast simulation of a generic collider experiment

  https://cp3.irmp.ucl.ac.be/projects/delphes

- **Pythia8 8.307**: A tool for the generation of events in high-energy collisions

   http://home.thep.lu.se/Pythia/

- **HepMC2 2.06.11**: A C++ Event Record for Monte Carlo Generators

  http://hepmc.web.cern.ch/hepmc/



## A. Conda

We recommend to install either Miniforge3 or Mambaforge from https://github.com/conda-forge/miniforge. Read the sections, [Download](https://github.com/conda-forge/miniforge#download) and [Install](https://github.com/conda-forge/miniforge#download).

- **Miniforge3**: conda with conda-forge channel
- **Mambaforge**: mamba (C++ implementation of conda) with conda-forge channel



## B. Conda Environment

Create a conda environment with the name, e.g., `delphes`.

- You may drop the channel information `-c conda-forge` in Miniforge3 or Mambaforge.

```bash
$ conda create -n delphes -c conda-forge root=6.26.10 lhapdf rsync
$ conda activate delphes
```



## C. Delphes, Pythia8, HepMC2 Packages

Download the following three conda packages from https://github.com/chofchof/delphes-conda/tree/main/conda-bld/linux-64.

If ROOT is installed from conda-forge, `pythia8` package is also installed by dependency. Since this `pythia8` does not work with MadGraph5, we need to prepare patched versions of `pythia8` and `hepmc2`. However, `delphes` does not require those patched versions.

- **[delphes-3.5.0-h3fd9d12_0.tar.bz2](https://github.com/chofchof/delphes-conda/raw/main/conda-bld/linux-64/delphes-3.5.0-h3fd9d12_0.tar.bz2)**
  - No dependency on the Python version.
  - Remove `external/` in examples. See `delphes-feedstock/recipe/patches/delphes-3.5.0_remove_external.patch` for details.
  - Notice that fj-contrib packages are installed in `$CONDA_PREFIX/include/fastjet/contribs/` as the original delphes.
- **[pythia8-8.307-py311h3fd9d12_1.tar.bz2](https://github.com/chofchof/delphes-conda/raw/main/conda-bld/linux-64/pythia8-8.307-py311h3fd9d12_1.tar.bz2)** (Python 3.11) or **[pythia8-8.307-py310h3fd9d12_1.tar.bz2](https://github.com/chofchof/delphes-conda/raw/main/conda-bld/linux-64/pythia8-8.307-py310h3fd9d12_1.tar.bz2)** (Python 3.10)
  - It has a dependency on the Python version, since it contains a Python wrapper which can be used by `import pythia8`.
  - A plugin `JetMatching.h` for MadGraph5 is included in `$CONDA_PREFIX/include/Pythia8Plugins/`.
  - Add `--cxx-common='-ldl -fPIC -lstdc++ -std=c++11 -pthread -O2 -DHEPMC2HACK'` to `configure` for MadGraph5.
- **[hepmc2-2.06.11-h3fd9d12_1.tar.bz2](https://github.com/chofchof/delphes-conda/raw/main/conda-bld/linux-64/hepmc2-2.06.11-h3fd9d12_1.tar.bz2)**
  - No dependency on the Python version.
  - Modify `src/WeightContainer.cc` and `HepMC/WeightContainer.h` for MadGraph5. See `hepmc2-feedstock/recipe/patches/HepMC-2.06.11-madgraph5.patch` for details.

```bash
(delphes)$ conda install delphes-3.5.0-h3fd9d12_0.tar.bz2 pythia8-8.307-py311h3fd9d12_1.tar.bz2 hepmc2-2.06.11-h3fd9d12_1.tar.bz2
(delphes)$ cat > $CONDA_PREFIX/conda-meta/pinned
root==6.26.10
delphes==3.5.0
pythia8==8.307
hepmc==2.06.11
(CTRL-D)
(delphes)$ conda update --all -y
```



## D. MadGraph5

https://launchpad.net/mg5amcnlo

### Installation

Download https://launchpad.net/mg5amcnlo/3.0/3.4.x/+download/MG5_aMC_v3.4.2.tar.gz.

```bash
(delphes)$ tar xvfz MG5_aMC_v3.4.2.tar.gz
(delphes)$ cd MG5_aMC_v3_4_2
(delphes)$ sed -i -e "70cpythia8_path = $CONDA_PREFIX" -e "173clhapdf_py3 = lhapdf-config" input/mg5_configuration.txt
(delphes)$ sed -i -e '105c\ \ llhapdf+= $(shell $(lhapdf) --cflags --libs) -lLHAPDF $(STDLIB)' Template/LO/Source/.make_opts
(delphes)$ bin/mg5_aMC
MG5_aMC>install mg5amc_py8_interface
   You are installing 'mg5amc_py8_interface', please cite ref(s): arXiv:1410.3012, arXiv:XXXX.YYYYY.
...(skip)...
MG5_aMC>quit
```

- MadGraph5 (3.4.2) has a conflict with `lhapdf` if it is installed from conda-forge. Compile-time error occurs when `pdlabel` is set to `lhapdf` in `run_card.dat`. To solve this problem, `Template/LO/Source/.make_opts` must be modified to add `$(STDLIB)` as above.

### Test

#### Generate Events (p p > z z)

```bash
(delphes)$ bin/mg5_aMC
MG5_aMC>generate p p > z z
MG5_aMC>output ../pp_zz
MG5_aMC>launch
> 1 (set shower = Pythia8)
> 0 (done)
> 2 (run_card.dat #line 47 & 48: lhapdf = pdlabel, 315000 = lhaid)
> 0 (done)
...(skip)...
  === Results Summary for run: run_01 tag: tag_1 ===

     Cross-section :   10.79 +- 0.01684 pb
     Nb of events :  10000

INFO: storing files of previous run
INFO: Storing Pythia8 files of previous run
INFO: Done
...(skip)...
MG5_aMC> quit
(delphes)$ cd ..
(delphes)$ ls -al pp_zz/Events/run_01/
total 800872
drwxr-xr-x 2 chof chof      4096 Apr 10 13:34 .
drwxr-xr-x 3 chof chof      4096 Apr 10 13:31 ..
-rw-r--r-- 1 chof chof      7295 Apr 10 13:31 log_sys_0.txt
-rw-r--r-- 1 chof chof      7292 Apr 10 13:31 log_sys_1.txt
-rw-r--r-- 1 chof chof      7294 Apr 10 13:31 log_sys_2.txt
-rw-r--r-- 1 chof chof      7289 Apr 10 13:31 log_sys_3.txt
-rw-r--r-- 1 chof chof      7276 Apr 10 13:31 parton_systematics.log
-rw-r--r-- 1 chof chof     23427 Apr 10 13:32 run_01_tag_1_banner.txt
-rwxr--r-- 1 chof chof       226 Apr 10 13:31 run_shower.sh
-rw-r--r-- 1 chof chof    774497 Apr 10 13:32 tag_1_djrs.dat
-rw-r--r-- 1 chof chof    774489 Apr 10 13:32 tag_1_pts.dat
-rw-r--r-- 1 chof chof      5765 Apr 10 13:31 tag_1_pythia8.cmd
-rw-r--r-- 1 chof chof   1593862 Apr 10 13:32 tag_1_pythia8.log
-rw-r--r-- 1 chof chof 806811284 Apr 10 13:32 tag_1_pythia8_events.hepmc.gz
-rw-r--r-- 1 chof chof  10035134 Apr 10 13:31 unweighted_events.lhe.gz
```

 

## E. Delphes for Python

Reference: https://cp3.irmp.ucl.ac.be/projects/delphes/wiki/WorkBook/QuickTour



### Running Delphes

When running Delphes without parameters or when supplying an invalid command line, the following message will be shown:

```bash
(delphes)$ DelphesHepMC3
 Usage: DelphesHepMC3 config_file output_file [input_file(s)]
 config_file - configuration file in Tcl format,
 output_file - output file in ROOT format,
 input_file(s) - input file(s) in HepMC format,
 with no input_file, or when input_file is -, read standard input.
```

Running Delphes with HepMC input files:

```bash
(delphes)$ curl -O http://cp3.irmp.ucl.ac.be/~demin/test.hepmc3.gz
(delphes)$ rm -f delphes_output.root
(delphes)$ gunzip -c test.hepmc3.gz | DelphesHepMC3 $CONDA_PREFIX/share/delphes/cards/delphes_card_CMS.tcl delphes_output.root
...(skip)...
** Reading standard input
** 1000 events processed
** Exiting...
```

Running Delphes with files accessible via HTTP:

```bash
(delphes)$ rm -f ../delphes_output.root
(delphes)$ curl http://cp3.irmp.ucl.ac.be/~demin/test.hepmc3.gz | gunzip | ./DelphesHepMC3 cards/delphes_card_CMS.tcl ../delphes_output.root
...(skip)...
** 1000 events processed
** Exiting...
```



#### Analyzing Delphes Output

Delphes output can be analyzed with the ROOT data analysis framework. This can be done in simple cases with `TTree::Draw`, or with macros for more advanced cases. Examples and mini analysis frameworks are provided in C++ (using ExRootAnalysis) and Python (using [DelphesAnalysis](https://cp3.irmp.ucl.ac.be/projects/delphes/wiki/WorkBook/DelphesAnalysis)).



##### Simple analysis using `TTree::Draw`

Start ROOT and load Delphes shared library:

```bash
(delphes)$ ipython
Python 3.11.3 | packaged by conda-forge | (main, Apr  6 2023, 08:57:19) [GCC 11.3.0]
Type 'copyright', 'credits' or 'license' for more information
IPython 8.12.0 -- An enhanced Interactive Python. Type '?' for help.

In [1]: import ROOT

In [2]: ROOT.gSystem.Load("libDelphes")
Installed ROOT event loop hook.
Out[2]: 0
```

Open ROOT tree file and do some basic analysis using `Draw` or `TBrowser`:

```bash
In [3]: f = ROOT.TFile.Open("delphes_output.root")

In [4]: f.Get("Delphes").Draw("Jet.PT")
Info in <TCanvas::MakeDefCanvas>:  created default TCanvas with name c1

In [5]: browser = ROOT.TBrowser()

In [6]: quit
```

- Note 1: `Delphes` - tree name, it can be learnt e.g. from `TBrowser`

- Note 2: `Jet` - branch name; `PT` - variable (leaf) of this branch

- From the ROOT Object Browser window, double click

  `ROOT Files > delphes_output.root > Delphes > Jet > Jet.PT`

  to get the same histogram plot.

Complete description of all branches can be found at [WorkBook/RootTreeDescription](https://cp3.irmp.ucl.ac.be/projects/delphes/wiki/WorkBook/RootTreeDescription)



##### Macro-based analysis

The [examples](https://cp3.irmp.ucl.ac.be/projects/delphes/browser/examples) directory contains a basic ROOT analysis macro called [Example1.C](https://cp3.irmp.ucl.ac.be/projects/delphes/browser/examples/Example1.C). This ROOT analysis macro consists of histogram booking, event loop (histogram filling), histogram display.

Here are commands to run this macro:

```bash
(delphes)$ root
root [0] gSystem->Load("libDelphes");
root [1] .X $CONDA_PREFIX/share/delphes/examples/Example1.C("delphes_output.root")
...(skip)...
Jet pt: 26.1661
Jet pt: 24.7914
Info in <TCanvas::MakeDefCanvas>:  created default TCanvas with name c1
root [2] .q
```

It is also possible to run `examples/Example1.py` as follows:

```bash
(delphes)$ python $CONDA_PREFIX/share/delphes/examples/Example1.py delphes_output.root
...(skip)...
Jet pt: 26.1661434173584
Jet pt: 24.791427612304688
Info in <TCanvas::MakeDefCanvas>:  created default TCanvas with name c1
Press Enter to continue...
```



##### More advanced macro-based analysis

The [examples](https://cp3.irmp.ucl.ac.be/projects/delphes/browser/examples) directory contains a ROOT macro called [Example2.C](https://cp3.irmp.ucl.ac.be/projects/delphes/browser/examples/Example2.C) demonstrating how to use class `ExRootTreeReader` to access data and class `ExRootResult` to manage histograms booking and output.

This macro can be run by python with `examples/Example2.py` as follows:

```bash
(delphes)$ cd examples
(delphes)$ python Example2.py delphes_output.root
** Chain contains 1000 events
Info in <TCanvas::Print>: file jet_pt_0.png has been created
Info in <TCanvas::Print>: file jet_pt_1.png has been created
Info in <TCanvas::Print>: file jet_pt_all.png has been created
Info in <TCanvas::Print>: file electron_pt.png has been created
Info in <TCanvas::Print>: file missing_et.png has been created
** Exiting...
(delphes)$ ls *.png
electron_pt.png  jet_pt_0.png  jet_pt_1.png  jet_pt_all.png  missing_et.png
```



##### Analysis in Python

[DelphesAnalysis](https://cp3.irmp.ucl.ac.be/projects/delphes/wiki/WorkBook/DelphesAnalysis) is an analysis framework written in Python where a clear separation is maintained between the standard code and what the user has to implement. This makes it easy to apprehend and generic, still retaining full flexibility and scalability. It is configured in a single configuration file.

More details and examples on the [dedicated page](https://cp3.irmp.ucl.ac.be/projects/delphes/wiki/WorkBook/DelphesAnalysis).
