compile: dataMemo.txt
	vcs -sverilog -debug_pp +vcs+vcdpluson axi4_types.sv axi4_lite_if.sv AXI_rom.sv AXI4l_slavedecerr.sv axi_master.sv axi_addrmap.sv axi4l_interconnect.sv AXI_master_top.sv -R
waves:
	dve -vpd  vcdplus.vpd &
dataMemo.txt:
	./dataMemoria
clean: 
	rm -rf csrc simv.daidir vcdplus.vpd simv ucli.key DVEfiles dataMemo.txt
