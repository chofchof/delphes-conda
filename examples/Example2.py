#!/usr/bin/env python

"""
Simple macro showing how to access branches from the delphes output root file,
loop over events, store histograms in a root file and print them as image files.

root -l examples/Example2.C'("delphes_output.root")'
"""

import ROOT

ROOT.gSystem.Load("libDelphes")

from ROOT import TChain, TH1, kRed, kBlue, nullptr
from ROOT import ExRootTreeReader, ExRootResult


from dataclasses import dataclass, field

@dataclass
class MyPlots:
    f_jet_pt: list[TH1] = field(default_factory=list)
    f_missing_e: TH1 = nullptr
    f_electron_pt: TH1 = nullptr


def book_histograms(result: ExRootResult, plots: MyPlots) -> None:
    # book 2 histograms for PT of 1st and 2nd leading jets
    plots.f_jet_pt.append(
        result.AddHist1D(
            "jet_pt_0", "leading jet P_{T}",
            "jet P_{T}, GeV/c", "number of jets",
            50, 0.0, 100.0
        )
    )
    plots.f_jet_pt.append(
        result.AddHist1D(
            "jet_pt_1", "2nd leading jet P_{T}",
            "jet P_{T}, GeV/c", "number of jets",
            50, 0.0, 100.0
        )
    )
    plots.f_jet_pt[0].SetLineColor(kRed)
    plots.f_jet_pt[1].SetLineColor(kBlue)

    # book 1 stack of 2 histograms and legend for stack of 2 histograms
    stack = result.AddHistStack("jet_pt_all", "1st and 2nd jets P_{T}")
    legend = result.AddLegend(0.72, 0.86, 0.98, 0.98)
    for hist, title in zip(plots.f_jet_pt, ["leading jet", "second jet"]):
        stack.Add(hist)
        legend.AddEntry(hist, title, "l")
    # attach legend to stack (legend will be printed over stack in .eps file)
    result.Attach(stack, legend)

    # book more histograms
    plots.f_electron_pt = result.AddHist1D(
        "electron_pt", "electron P_{T}",
        "electron P_{T}, GeV/c", "number of electrons",
        50, 0.0, 100.0
    )
    plots.f_missing_et = result.AddHist1D(
        "missing_et", "Missing E_{T}",
        "Missing E_{T}, GeV", "number of events",
        60, 0.0, 30.0
    )

    # book general comment
    comment = result.AddComment(0.64, 0.86, 0.98, 0.98)
    comment.AddText("demonstration plot")
    comment.AddText("produced by Example2.py")

    # attach comment to single histograms
    for hist in plots.f_jet_pt:
        result.Attach(hist, comment)
    result.Attach(plots.f_electron_pt, comment)

    # show histogram statisics for MissingET
    plots.f_missing_et.SetStats()


def analyse_events(tree_reader: ExRootTreeReader, plots: MyPlots) -> None:
    branch_jet = tree_reader.UseBranch("Jet")
    branch_electron = tree_reader.UseBranch("Electron")
    branch_missing_et = tree_reader.UseBranch("MissingET")

    all_entries = tree_reader.GetEntries()

    print(f"** Chain contains {all_entries} events")

    # Loop over all events
    for entry in range(all_entries):
        # Load selected branches with data from specified event
        tree_reader.ReadEntry(entry)

        # Analyse two leading jets
        if branch_jet.GetEntriesFast() >= 2:
            plots.f_jet_pt[0].Fill(branch_jet.At(0).PT)
            plots.f_jet_pt[1].Fill(branch_jet.At(1).PT)

        # Analyse missing ET
        if branch_missing_et.GetEntriesFast() > 0:
            plots.f_missing_et.Fill(branch_missing_et.At(0).MET)

        # Loop over all electrons in event
        for electron in branch_electron:
            plots.f_electron_pt.Fill(electron.PT)


def print_histograms(result: ExRootResult, plots: MyPlots) -> None:
    result.Print("png")


def run_example2(input_file: str) -> None:
    # Create chain of root trees
    chain = TChain("Delphes")
    chain.Add(input_file)

    # Create object of class ExRootTreeReader and ExRootResult
    tree_reader = ExRootTreeReader(chain)
    result = ExRootResult()

    plots = MyPlots()

    book_histograms(result, plots)
    analyse_events(tree_reader, plots)
    print_histograms(result, plots)

    result.Write("results.root")
    print("** Exiting...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(" Usage: Example2.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]
    run_example2(input_file)
