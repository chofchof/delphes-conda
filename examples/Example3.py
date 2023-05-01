#!/usr/bin/env python

"""
This macro shows how to access the particle-level reference for reconstructed objects.
It is also shown how to loop over the jet constituents.

root -l examples/Example3.C'("delphes_output.root")'
"""

import ROOT

ROOT.gSystem.Load("libDelphes")

from ROOT import TChain, TH1, TLorentzVector, nullptr
from ROOT import ExRootTreeReader, ExRootResult


from dataclasses import dataclass

@dataclass
class TestPlots:
    f_electron_delta_pt: TH1 = nullptr
    f_electron_delta_eta: TH1 = nullptr

    f_photon_delta_pt: TH1 = nullptr
    f_photon_delta_eta: TH1 = nullptr
    f_photon_delta_e: TH1 = nullptr

    f_muon_delta_pt: TH1 = nullptr
    f_muon_delta_eta: TH1 = nullptr

    f_jet_delta_pt: TH1 = nullptr


def book_histograms(result: ExRootResult, plots: TestPlots) -> None:
    plots.f_electron_delta_pt = result.AddHist1D(
        "electron_delta_pt", "(p_{T}^{particle} - p_{T}^{electron})/p_{T}^{particle}",
        "(p_{T}^{particle} - p_{T}^{electron})/p_{T}^{particle}", "number of electrons",
        100, -0.1, 0.1
    )
    plots.f_electron_delta_eta = result.AddHist1D(
        "electron_delta_eta", "(#eta^{particle} - #eta^{electron})/#eta^{particle}",
        "(#eta^{particle} - #eta^{electron})/#eta^{particle}", "number of electrons",
        100, -0.1, 0.1
    )
    plots.f_photon_delta_pt = result.AddHist1D(
        "photon_delta_pt", "(p_{T}^{particle} - p_{T}^{photon})/p_{T}^{particle}",
        "(p_{T}^{particle} - p_{T}^{photon})/p_{T}^{particle}", "number of photons",
        100, -0.1, 0.1
    )
    plots.f_photon_delta_eta = result.AddHist1D(
        "photon_delta_eta", "(#eta^{particle} - #eta^{photon})/#eta^{particle}",
        "(#eta^{particle} - #eta^{photon})/#eta^{particle}", "number of photons",
        100, -0.1, 0.1
    )
    plots.f_photon_delta_e = result.AddHist1D(
        "photon_delta_energy", "(E^{particle} - E^{photon})/E^{particle}",
        "(E^{particle} - E^{photon})/E^{particle}", "number of photons",
        100, -0.1, 0.1
    )
    plots.f_muon_delta_pt = result.AddHist1D(
        "muon_delta_pt", "(p_{T}^{particle} - p_{T}^{muon})/p_{T}^{particle}",
        "(p_{T}^{particle} - p_{T}^{muon})/p_{T}^{particle}", "number of muons",
        100, -0.1, 0.1
    )
    plots.f_muon_delta_eta = result.AddHist1D(
        "muon_delta_eta", "(#eta^{particle} - #eta^{muon})/#eta^{particle}",
        "(#eta^{particle} - #eta^{muon})/#eta^{particle}", "number of muons",
        100, -0.1, 0.1
    )
    plots.f_jet_delta_pt = result.AddHist1D(
        "jet_delta_pt", "(p_{T}^{jet} - p_{T}^{constituents})/p_{T}^{jet}",
        "(p_{T}^{jet} - p_{T}^{constituents})/p_{T}^{jet}", "number of jets",
        100, -1.0e-1, 1.0e-1
    )


def analyse_events(tree_reader: ExRootTreeReader, plots: TestPlots) -> None:
    branch_particle = tree_reader.UseBranch("Particle")
    branch_electron = tree_reader.UseBranch("Electron")
    branch_photon = tree_reader.UseBranch("Photon")
    branch_muon = tree_reader.UseBranch("Muon")
    branch_e_flow_track = tree_reader.UseBranch("EFlowTrack")
    branch_e_flow_photon = tree_reader.UseBranch("EFlowPhoton")
    branch_e_flow_neutral_hadron = tree_reader.UseBranch("EFlowNeutralHadron")
    branch_jet = tree_reader.UseBranch("Jet")

    all_entries = tree_reader.GetEntries()

    print(f"** Chain contains {all_entries} events")

    # Loop over all events
    for entry in range(all_entries):
        # Load selected branches with data from specified event
        tree_reader.ReadEntry(entry)

        # Loop over all electrons in event
        for electron in branch_electron:
            particle = electron.Particle.GetObject()
            plots.f_electron_delta_pt.Fill((particle.PT - electron.PT) / particle.PT)
            plots.f_electron_delta_eta.Fill((particle.Eta - electron.Eta) / particle.Eta)

        # Loop over all photons in event
        for photon in branch_photon:
            # skip photons with references to multiple particles
            if photon.Particles.GetEntriesFast() != 1:
                continue
            particle = photon.Particles.At(0)
            plots.f_photon_delta_pt.Fill((particle.PT - photon.PT) / particle.PT)
            plots.f_photon_delta_eta.Fill((particle.Eta - photon.Eta) / particle.Eta)
            plots.f_photon_delta_e.Fill((particle.E - photon.E) / particle.E)

        # Loop over all muons in event
        for muon in branch_muon:
            particle = muon.Particle.GetObject()
            plots.f_muon_delta_pt.Fill((particle.PT - muon.PT) / particle.PT)
            plots.f_muon_delta_eta.Fill((particle.Eta - muon.Eta) / particle.Eta)

        #print("-- New event --")

        # Loop over all jets in event
        for jet in branch_jet:
            momentum = TLorentzVector(0.0, 0.0, 0.0, 0.0)
            #print(f"Looping over jet constituents. Jet pt: {jet.PT}, eta: {jet.Eta}, phi: {jet.Phi}")
            # Loop over all jet's constituents
            for obj in jet.Constituents:
                # Check if the constituent is accessible
                if not obj:
                    continue
                momentum += obj.P4()

                #_eta = obj.Eta
                #_phi = obj.Phi
                #if isinstance(obj, ROOT.GenParticle):
                #    _name = "GenPart"
                #    _pt = obj.PT
                #elif isinstance(obj, ROOT.Track):
                #    _name = "Track"
                #    _pt = obj.PT
                #elif isinstance(obj, ROOT.Tower):
                #    _name = "Tower"
                #    _pt = obj.ET
                #print(f"    {_name} pt: {_pt}, eta: {_eta}, phi: {_phi}")

            plots.f_jet_delta_pt.Fill((jet.PT - momentum.Pt()) / jet.PT)


def print_histograms(result: ExRootResult, plots: TestPlots) -> None:
    result.Print("png")


def run_example3(input_file: str) -> None:
    # Create chain of root trees
    chain = TChain("Delphes")
    chain.Add(input_file)

    # Create object of class ExRootTreeReader and ExRootResult
    tree_reader = ExRootTreeReader(chain)
    result = ExRootResult()

    plots = TestPlots()

    book_histograms(result, plots)
    analyse_events(tree_reader, plots)
    print_histograms(result, plots)

    result.Write("results.root")
    print("** Exiting...")


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 2:
        print(" Usage: Example3.py input_file")
        sys.exit(1)

    input_file = sys.argv[1]
    run_example3(input_file)
