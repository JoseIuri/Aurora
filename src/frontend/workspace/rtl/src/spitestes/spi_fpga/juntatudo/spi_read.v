module spi_read(axi4_lite_if rti,
					 inout IO0,
					 inout IO1,
					 inout IO2,
					 inout IO3,
					 input logic enable,
					 output logic CS,
					 output logic spi_clk);

	master_spi teste_master (.master(rti), .enable(enable));
   spi teste (.busmem(rti), .IO0(IO0), .IO1(IO1), .IO2(IO2), .IO3(IO3), .CS(CS), .CLOCK(spi_clk), .enable(enable));

endmodule
