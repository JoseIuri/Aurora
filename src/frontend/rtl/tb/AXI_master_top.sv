module time_unit;
  initial $timeformat(-9,1," ns",9);
endmodule

module AXI_master_top();

	logic ACLK, ARESETn;
	logic [1:0]delay;

	logic [1:0]select1, select2;
	logic [9:0]addr1, addr2;

	axi4_lite_if #(.ADDR_SIZE(12)) masterbus(.ACLK(ACLK),.ARESETn(ARESETn));
	axi4_lite_if #(.ADDR_SIZE(10)) slavebus[3:0](.ACLK(ACLK),.ARESETn(ARESETn));

	AXI_rom rom0(.rif(slavebus[0]));
	AXI_rom rom1(.rif(slavebus[1]));

	AXI4l_slavedecerr decerr1(.slavedecerr(slavebus[2]));
	AXI4l_slavedecerr decerr2(.slavedecerr(slavebus[3]));

	axi_master master(.axibus(masterbus),.delay(delay));

	axi_addrmap #(.ADDR_SIZE(12), .SELECT(2)) read_addr_map (.address_in(masterbus.araddr),.address_out(addr1),.select(select1));
	axi_addrmap #(.ADDR_SIZE(12), .SELECT(2)) write_addr_map (.address_in(masterbus.awaddr),.address_out(addr2),.select(select2));

	
	axi4l_interconnect #(.DATA_SIZE(32), .ADDR_SIZE(10), .SLAVES(4)) inter (.master(masterbus), .slave(slavebus),
	.selectread(read_addr_map.select),.selectwrite(write_addr_map.select), .addrread(read_addr_map.address_out), .addrwrite(write_addr_map.address_out));

	always #10 ACLK = ~ACLK;

	initial begin
		//$vcdplusmemon;
		ACLK = 0;
		ARESETn = 0;
		#5 ACLK = 1'b1;
        #5 ACLK = 1'b0;
		@(posedge ACLK);
		ARESETn = 1;
		delay =1;/* $urandom % 5;*/
	end		
	initial
	#500 $finish;


endmodule