from chimera import runCommand as rc

rc('open {protein} {ligand}')
rc('select #1 zr<15')
rc('write format mol2 selected #0 {active_site}')
