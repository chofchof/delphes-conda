#!/usr/bin/env python

"""
Python translation of DelphesPythia8 written by Jin-Hwan CHO
"""

# PyROOT + Delphes + Pythia8

import ROOT
from ROOT import TDatabasePDG, TFile, TMath, TObjArray, TParticlePDG

ROOT.gSystem.Load("libDelphes")
from ROOT import Candidate, Delphes, DelphesFactory, HepMCEvent, LHEFEvent, LHEFWeight, TStopwatch
from ROOT import ExRootConfReader, ExRootProgressBar, ExRootTreeBranch, ExRootTreeWriter

ROOT.gInterpreter.Declare('#include "classes/DelphesLHEFReader.h"')
from ROOT import DelphesLHEFReader

# Reference: https://root-forum.cern.ch/t/segmentation-fault-in-pyroot-pythia8/54747
# 1. Warning: `pythia.info.weight()` causes segmentation violation
#    with `from ROOT import Pythia8 as pythia8`.
# 2. However, `pythia.infoPython().weight()` has no problem
#    with `import pythia8`.
import pythia8

ROOT.gROOT.SetBatch()


# Standard libraries
import os, sys, math

# Reference: https://cffi.readthedocs.io/en/latest/ref.html#support-for-file
def _fopen(input_file: str, mode: str) -> ROOT._IO_FILE | None:
    if input_file == "-": # stdin
        fd = sys.stdin.fileno()
    else:
        try:
            with open(input_file, "rb") as fp:
                fd = os.dup(fp.fileno())
        except:
            return None
   
    fp = ROOT.fdopen(fd, mode)
    return fp


def ConvertInput(
    eventCounter: int,
    pythia: pythia8.Pythia,
    branch: ExRootTreeBranch,
    factory: DelphesFactory,
    allParticleOutputArray: TObjArray,
    stableParticleOutputArray: TObjArray,
    partonOutputArray: TObjArray,
    readStopwatch: TStopwatch,
    procStopwatch: TStopwatch
) -> None:

    # event information
    # element: HepMCEvent = ROOT.bind_object(
    #     ROOT.addressof(branch.NewEntry()),
    #     HepMCEvent
    # )
    element: HepMCEvent = branch.NewEntry()

    element.Number = eventCounter

    pythia_info: pythia8.Info = pythia.infoPython() # import pythia8

    element.ProcessID = pythia_info.code()
    element.MPI = 1
    element.Weight = pythia_info.weight()
    element.Scale = pythia_info.QRen()
    element.AlphaQED = pythia_info.alphaEM()
    element.AlphaQCD = pythia_info.alphaS()

    element.ID1 = pythia_info.id1()
    element.ID2 = pythia_info.id2()
    element.X1 = pythia_info.x1()
    element.X2 = pythia_info.x2()
    element.ScalePDF = pythia_info.QFac()
    element.PDF1 = pythia_info.pdf1()
    element.PDF2 = pythia_info.pdf2()

    element.ReadTime = readStopwatch.RealTime()
    element.ProcTime = procStopwatch.RealTime()

    pdg: TDatabasePDG = TDatabasePDG.Instance();

    for i in range(1, pythia.event.size()):
        particle: pythia8.Particle = pythia.event[i]

        pid: int = particle.id()
        status: int = particle.statusHepMC()
        px: float = particle.px()
        py: float = particle.py()
        pz: float = particle.pz()
        e: float = particle.e()
        mass: float = particle.m()
        x: float = particle.xProd()
        y: float = particle.yProd()
        z: float = particle.zProd()
        t: float = particle.tProd()

        candidate: Candidate = factory.NewCandidate()

        candidate.PID = pid
        pdgCode: int = TMath.Abs(candidate.PID)

        candidate.Status = status

        candidate.M1 = particle.mother1() - 1
        candidate.M2 = particle.mother2() - 1

        candidate.D1 = particle.daughter1() - 1
        candidate.D2 = particle.daughter2() - 1

        pdgParticle: TParticlePDG = pdg.GetParticle(pid)
        candidate.Charge = int(pdgParticle.Charge() / 3.0) if pdgParticle else -999
        candidate.Mass = mass

        candidate.Momentum.SetPxPyPzE(px, py, pz, e)

        candidate.Position.SetXYZT(x, y, z, t)

        allParticleOutputArray.Add(candidate)

        if not pdgParticle:
            continue

        if status == 1:
            stableParticleOutputArray.Add(candidate)
        elif pdgCode <= 5 or pdgCode == 21 or pdgCode == 15:
            partonOutputArray.Add(candidate)


"""
Single-particle gun. The particle must be a colour singlet.
Input: flavour, energy, direction (theta, phi).
If theta < 0 then random choice over solid angle.
Optional final argument to put particle at rest => E = m.
from pythia8 example 21
"""

def fillParticle(
    id: int, pMax: float, etaMax: float,
    event: pythia8.Event, pdt: pythia8.ParticleData, rndm: pythia8.Rndm
) -> None:
    
    #Reset event record to allow for new event.
    event.reset()

    # Generate uniform pt and eta.

    # pMin = 0.1 GeV for single particles
    pp: float = math.pow(10, -1.0 + (math.log10(pMax) + 1.0) * rndm.flat())
    eta: float = (2.0 * rndm.flat() - 1.0) * etaMax
    phi: float = 2.0 * math.pi * rndm.flat()
    mm: float = pdt.mSel(id)
    ee: float = pythia8.sqrtpos(pp * pp + mm * mm);
    pt: float = pp / math.cosh(eta)

    # Store the particle in the event record.
    event.append(id, 1, 0, 0, pt * math.cos(phi), pt * math.sin(phi), pt * math.sinh(eta), ee, mm)


def fillPartons(
    id: int, pMax: float, etaMax: float,
    event: pythia8.Event, pdt: pythia8.ParticleData, rndm: pythia8.Rndm
) -> None:
    
    # Reset event record to allow for new event.
    event.reset()

    # Generate uniform pt and eta.

    # pMin = 1 GeV for jets
    pp: float = math.pow(10, math.log10(pMax) * rndm.flat())
    eta: float = (2.0 * rndm.flat() - 1.0) * etaMax
    phi: float = 2.0 * math.pi * rndm.flat()
    mm: float = pdt.mSel(id)
    ee: float = pythia8.sqrtpos(pp * pp + mm * mm)
    pt: float = pp / math.cosh(eta)

    if (id == 4 or id == 5) and pt < 10.0:
        return

    if id == 21:
        event.append(21, 23, 101, 102, pt * math.cos(phi), pt * math.sin(phi), pt * math.sinh(eta), ee)
        event.append(21, 23, 102, 101, -pt * math.cos(phi), -pt * math.sin(phi), -pt * math.sinh(eta), ee)
    else:
        event.append(id, 23, 101, 0, pt * math.cos(phi), pt * math.sin(phi), pt * math.sinh(eta), ee, mm)
        event.append(-id, 23, 0, 101, -pt * math.cos(phi), -pt * math.sin(phi), -pt * math.sinh(eta), ee, mm)


def run_main(config_file: str, pythia_card: str, output_file: str) -> None:

    try:
        outputFile: TFile = TFile.Open(output_file, "CREATE")
    except:
        raise RuntimeError(f"can't create output file {output_file}")

    treeWriter: ExRootTreeWriter = ExRootTreeWriter(outputFile, "Delphes")

    branchEvent: ExRootTreeBranch = treeWriter.NewBranch("Event", HepMCEvent.Class())

    confReader: ExRootConfReader = ExRootConfReader()
    confReader.ReadFile(config_file)

    modularDelphes: Delphes = Delphes("Delphes")
    modularDelphes.SetConfReader(confReader)
    modularDelphes.SetTreeWriter(treeWriter)

    factory: DelphesFactory = modularDelphes.GetFactory()
    allParticleOutputArray: TObjArray = modularDelphes.ExportArray("allParticles")
    stableParticleOutputArray: TObjArray = modularDelphes.ExportArray("stableParticles")
    partonOutputArray: TObjArray = modularDelphes.ExportArray("partons")

    # Initialize Pythia
    try:
        pythia: pythia8.Pythia = pythia8.Pythia()
    except:
        raise RuntimeError("can't create Pythia instance")

    # Warning: Pythia.readFile(s: raw string)
    if not pythia.readFile(pythia_card):
        raise RuntimeError(f"can't read Pythia8 configuration file {pythia_card}")

    # Extract settings to be used in the main program
    numberOfEvents: int = pythia.mode("Main:numberOfEvents")
    timesAllowErrors: int = pythia.mode("Main:timesAllowErrors")

    spareFlag1: bool = pythia.flag("Main:spareFlag1")
    spareMode1: int = pythia.mode("Main:spareMode1")
    spareParm1: float = pythia.parm("Main:spareParm1")
    spareParm2: float = pythia.parm("Main:spareParm2")

    # Check if particle gun
    reader: DelphesLHEFReader | None = None
    if not spareFlag1:
        inputFile = _fopen(pythia.word("Beams:LHEF"), "r")
        if inputFile:
            reader = DelphesLHEFReader()
            reader.SetInputFile(inputFile)

            branchEventLHEF: ExRootTreeBranch = treeWriter.NewBranch(
                "EventLHEF", LHEFEvent.Class()
            )
            branchWeightLHEF: ExRootTreeBranch = treeWriter.NewBranch(
                "WeightLHEF", LHEFWeight.Class()
            )

            allParticleOutputArrayLHEF: TObjArray = modularDelphes.ExportArray("allParticlesLHEF")
            stableParticleOutputArrayLHEF: TObjArray = modularDelphes.ExportArray("stableParticlesLHEF")
            partonOutputArrayLHEF: TObjArray = modularDelphes.ExportArray("partonsLHEF")

    modularDelphes.InitTask()

    pythia.init()

    progressBar: ExRootProgressBar = ExRootProgressBar(-1)

    readStopwatch: TStopwatch = TStopwatch()
    procStopwatch: TStopwatch = TStopwatch()

    # Loop over all objects
    errorCounter: int = 0
    treeWriter.Clear()
    modularDelphes.Clear()
    readStopwatch.Start()

    for eventCounter in range(numberOfEvents):
        while reader:
            _result = reader.ReadBlock(
                factory,
                allParticleOutputArrayLHEF,
                stableParticleOutputArrayLHEF,
                partonOutputArrayLHEF
            )
            if not _result or reader.EventReady():
                break

        if spareFlag1:
            if (spareMode1 >= 1 and spareMode1 <= 5) or spareMode1 == 21:
                fillPartons(
                    spareMode1, spareParm1, spareParm2, pythia.event, pythia.particleData, pythia.rndm
                )
            else:
                fillParticle(
                    spareMode1, spareParm1, spareParm2, pythia.event, pythia.particleData, pythia.rndm
                )

        if not pythia.next():
            # If failure because reached end of file then exit event loop
            if pythia.infoPython().atEndOfFile():
                sys.stderr.write("Aborted since reached end of Les Houches Event File\n")
                break

            # First few failures write off as "acceptable" errors, then quit
            errorCounter += 1
            if errorCounter > timesAllowErrors:
                sys.stderr.write("Event generation aborted prematurely, owing to error!\n")
                break

            modularDelphes.Clear()
            reader.Clear()
            continue

        readStopwatch.Stop()

        procStopwatch.Start()
        ConvertInput(
            eventCounter, pythia, branchEvent, factory,
            allParticleOutputArray, stableParticleOutputArray, partonOutputArray,
            readStopwatch, procStopwatch
        )
        modularDelphes.ProcessTask()
        procStopwatch.Stop()

        if reader:
            reader.AnalyzeEvent(branchEventLHEF, eventCounter, readStopwatch, procStopwatch)
            reader.AnalyzeWeight(branchWeightLHEF)

        treeWriter.Fill()
        treeWriter.Clear()

        modularDelphes.Clear()
        if reader:
            reader.Clear()

        readStopwatch.Start()
        progressBar.Update(eventCounter, eventCounter)

    progressBar.Update(eventCounter, eventCounter, True)
    progressBar.Finish()

    pythia.stat()

    modularDelphes.FinishTask()
    treeWriter.Write()

    print("** Exiting...")

    if inputFile:
        ROOT.fclose(inputFile)


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(f"""\
 Usage: python {sys.argv[0]} config_file pythia_card output_file
 config_file - configuration file in Tcl format,
 pythia_card - Pythia8 configuration file,
 output_file - output file in ROOT format."""
        )
        sys.exit(1)

    config_file: str = sys.argv[1]
    pythia_card: str = sys.argv[2]
    output_file: str = sys.argv[3]
    
    run_main(config_file, pythia_card, output_file)
