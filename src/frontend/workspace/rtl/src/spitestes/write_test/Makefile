compile: 
	vcs -sverilog -debug_pp +vcs+vcdpluson axi4_types.sv axi4_lite_if.sv master_spi.sv spi.sv mem.sv topteste.sv -R
waves:
	dve -vpd  vcdplus.vpd &

clean: 
	rm -rf csrc simv.daidir vcdplus.vpd simv ucli.key DVEfiles