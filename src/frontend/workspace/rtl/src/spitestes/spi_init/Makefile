compile: 
	vcs -sverilog -debug_pp +vcs+vcdpluson axi4_types.sv axi4_lite_if.sv spi_init.sv mem_init.sv topteste.sv -R
waves:
	dve -vpd  vcdplus.vpd &

clean: 
	rm -rf csrc simv.daidir vcdplus.vpd simv ucli.key DVEfiles
