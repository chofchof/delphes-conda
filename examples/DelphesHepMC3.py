#!/usr/bin/env python

"""
Python translation of DelphesHepMC3 written by Jin-Hwan CHO
"""

# PyROOT + Delphes

import ROOT
from ROOT import TFile, TObjArray

ROOT.gSystem.Load("libDelphes")
from ROOT import Delphes, DelphesFactory, HepMCEvent, Weight, TStopwatch
from ROOT import ExRootConfReader, ExRootProgressBar, ExRootTreeBranch, ExRootTreeWriter

ROOT.gInterpreter.Declare('#include "classes/DelphesHepMC3Reader.h"')
from ROOT import DelphesHepMC3Reader

ROOT.gROOT.SetBatch()


# Standard libraries
import os, sys

# Reference: https://cffi.readthedocs.io/en/latest/ref.html#support-for-file
def _fopen(input_file: str, mode: str) -> ROOT._IO_FILE:
    if input_file == "-": # stdin
        fd = sys.stdin.fileno()
    else:
        try:
            with open(input_file, "rb") as fp:
                fd = os.dup(fp.fileno())
        except:
            raise RuntimeError(f"can't open {input_file}")
   
    fp = ROOT.fdopen(fd, mode)
    return fp


def run_main(config_file: str, output_file: str, input_files: list[str]) -> None:

    try:
        outputFile = TFile.Open(output_file, "CREATE")
    except:
        raise RuntimeError(f"can't create output file {output_file}")

    treeWriter: ExRootTreeWriter = ExRootTreeWriter(outputFile, "Delphes")

    branchEvent: ExRootTreeBranch = treeWriter.NewBranch("Event", HepMCEvent.Class())
    branchWeight: ExRootTreeBranch = treeWriter.NewBranch("Weight", Weight.Class())

    confReader: ExRootConfReader = ExRootConfReader()
    confReader.ReadFile(config_file)

    maxEvents: int = confReader.GetInt("::MaxEvents", 0)
    skipEvents: int = confReader.GetInt("::SkipEvents", 0)

    if maxEvents < 0:
        raise RuntimeError("MaxEvents must be zero or positive")

    if skipEvents < 0:
        raise RuntimeError("SkipEvents must be zero or positive")

    modularDelphes: Delphes = Delphes("Delphes")
    modularDelphes.SetConfReader(confReader)
    modularDelphes.SetTreeWriter(treeWriter)

    factory: DelphesFactory = modularDelphes.GetFactory()
    allParticleOutputArray: TObjArray = modularDelphes.ExportArray("allParticles")
    stableParticleOutputArray: TObjArray = modularDelphes.ExportArray("stableParticles")
    partonOutputArray: TObjArray = modularDelphes.ExportArray("partons")

    reader: DelphesHepMC3Reader = DelphesHepMC3Reader()

    modularDelphes.InitTask()

    readStopwatch: TStopwatch = TStopwatch()
    procStopwatch: TStopwatch = TStopwatch()

    for input_file in input_files:

        if input_file == "-":
            print("** Reading standard input")
            inputFile = _fopen(input_file, "r")
            length: int = -1
        else:
            print(f"** Reading {input_file}")
            inputFile: ROOT._IO_FILE = _fopen(input_file, "r")

            ROOT.fseek(inputFile, 0, 2) # SEEK_END
            length: int = ROOT.ftello(inputFile)
            ROOT.fseek(inputFile, 0, 0) # SEEK_SET

            if length <= 0:
                ROOT.fclose(inputFile)
                continue

        reader.SetInputFile(inputFile)

        progressBar: ExRootProgressBar = ExRootProgressBar(length)

        # Loop over all objects
        eventCounter: int = 0
        treeWriter.Clear()
        modularDelphes.Clear()
        reader.Clear()
        readStopwatch.Start()

        while maxEvents <= 0 or eventCounter - skipEvents < maxEvents:
            _result: bool = reader.ReadBlock(
                factory,
                allParticleOutputArray,
                stableParticleOutputArray,
                partonOutputArray
            )
            if not _result: # failed to read block or end of the file
                break

            if reader.EventReady():
                eventCounter += 1
                readStopwatch.Stop()

                if eventCounter > skipEvents:
                    procStopwatch.Start()
                    modularDelphes.ProcessTask()
                    procStopwatch.Stop()

                    reader.AnalyzeEvent(branchEvent, eventCounter, readStopwatch, procStopwatch)
                    reader.AnalyzeWeight(branchWeight)

                    treeWriter.Fill()
                    treeWriter.Clear()

                modularDelphes.Clear()
                reader.Clear()
                readStopwatch.Start()

            progressBar.Update(ROOT.ftello(inputFile), eventCounter)

        ROOT.fseek(inputFile, 0, 2) # SEEK_END = 2
        progressBar.Update(ROOT.ftello(inputFile), eventCounter, True)
        progressBar.Finish()

        ROOT.fclose(inputFile)

    modularDelphes.FinishTask()
    treeWriter.Write()

    print("** Exiting...")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"""\
 Usage: python {sys.argv[0]} config_file output_file [input_file(s)]
 config_file - configuration file in Tcl format,
 output_file - output file in ROOT format,
 input_file(s) - input file(s) in HepMC format,
 with no input_file, or when input_file is -, read standard input."""
        )
        sys.exit(1)

    config_file: str = sys.argv[1]
    output_file: str = sys.argv[2]
    
    if len(sys.argv) > 3:
        input_files: list[str] = sys.argv[3:]
    else:
        input_files: list[str] = ["-"]

    run_main(config_file, output_file, input_files)