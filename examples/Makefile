all: Example1 Example2 Example3

Example1: delphes_output.root
	python $@.py $<

Example2: delphes_output.root
	python $@.py $<

Example3: delphes_output.root
	python $@.py $<

delphes_output.root: test.hepmc3.gz
	gunzip -c $< | DelphesSTDHEP ${CONDA_PREFIX}/share/delphes/cards/delphes_card_CMS.tcl $@

test.hepmc3.gz:
	curl -O http://cp3.irmp.ucl.ac.be/~demin/$@

clean:
	rm -f *.png results.root
