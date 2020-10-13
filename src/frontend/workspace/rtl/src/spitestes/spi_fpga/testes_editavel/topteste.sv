module time_unit;
  initial $timeformat(-9,1," ns",9);
endmodule

module top();

	//localparam ADDR_WIDTH = 10;
	//localparam DATA_WIDTH = 32;

	logic ACLK, ARESETn;
	axi4_lite_if #(.ADDR_SIZE(12)) bus(.ACLK(ACLK),.ARESETn(ARESETn));
	
	wire wire1,wire2,wire3,wire0;
	wire cs, clk;

	spi_test_init teste (.busmem(bus), .IO0(wire0), .IO1(wire1), .IO2(wire2), .IO3(wire3), .CS(cs), .CLOCK(clk), .flag_end(end_init), .estado(), .status_reg_lido1(), .status_reg_lido2());
	mem_test_init teste_mem (.busmem(bus),.IO0(wire0), .IO1(wire1), .IO2(wire2), .IO3(wire3), .CS(cs), .CLOCK(clk),.flag_end(end_init));

	always #10 ACLK = ~ACLK;

	initial begin
		$vcdplusmemon;
		ACLK = 0;

		ARESETn = 0; //Reset !
		#5 ACLK = 1'b1;
		#5 ACLK = 1'b0;

		@(posedge ACLK);
		
		ARESETn = 1;

	end
		
		initial
		#5000 $finish;


endmodule