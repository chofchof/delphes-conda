#!/usr/bin/env python

import ROOT

ROOT.gSystem.Load("libDelphes")

from ROOT import TChain, TH1F, ExRootTreeReader


def run_example1(input_file):
    # Create chain of root trees
    chain = TChain("Delphes")
    chain.Add(input_file)

    # Create object of class ExRootTreeReader
    tree_reader = ExRootTreeReader(chain)
    number_of_entries = tree_reader.GetEntries()

    # Get pointers to branches used in this analysis
    branch_jet = tree_reader.UseBranch("Jet")
    branch_electron = tree_reader.UseBranch("Electron")

    # Book histograms
    hist_jet_pt = TH1F("jet_pt", "jet P_{T}", 100, 0.0, 100.0)
    hist_mass = TH1F("mass", "M_{inv}(e_{1}, e_{2})", 100, 40.0, 140.0)

    # Loop over all events
    for entry in range(number_of_entries):
        # Load selected branches with data from specified event
        tree_reader.ReadEntry(entry)

        # If event contains at least 1 jet
        if branch_jet.GetEntries() > 0:
            # Take first jet
            jet = branch_jet.At(0)
            # Plot jet transverse momentum
            hist_jet_pt.Fill(jet.PT)
            # Print jet transverse momentum
            print(f"Jet pt: {jet.PT}")

        # If event contains at least 2 electrons
        if branch_electron.GetEntries() > 1:
            # Take first two electrons
            elec1 = branch_electron.At(0)
            elec2 = branch_electron.At(1)
            # Plot their invariant mass (ROOT::Math::LorentzVector)
            hist_mass.Fill((elec1.P4() + elec2.P4()).M())

    # Show resulting histograms
    hist_jet_pt.Draw()
    hist_mass.Draw()


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(" Usage: Example1.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]
    run_example1(input_file)

    try:
        input = raw_input
    except:
        pass

    input("Press Enter to continue...")
