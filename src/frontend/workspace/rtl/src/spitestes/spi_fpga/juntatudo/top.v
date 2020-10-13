module top(axi4_lite_if bus,
			  inout IO0,
			  inout IO1,
			  inout IO2,
			  inout IO3,
			  //input [1:0] sel,
			  output logic CS,
			  output spi_clk,
			  output flag_end_init,
			  input en_read,
			  input en_init,
			  output init_state,
			  output [7:0] regsta1
);

			  
spi_read read_module(
	.rti(bus),
	.IO0(IO0),
	.IO1(IO1),
	.IO2(IO2),
	.IO3(IO3),
	.enable(en_read),
	.CS(CS),
	.spi_clk(spi_clk)
	);
								
spi_init init_module(
	.busmem(bus),
	.IO0(IO0),
	.IO1(IO1),
	.IO2(IO2),
	.IO3(IO3),
	.enable(en_init),
	.CS(CS), 
	.CLOCK(spi_clk), 
	.flag_end_init(flag_end_init),
	.estado(init_state),
	.status_reg_lido(regsta1)
	);
	/*
   assign LEDR[0] = CLK;
   //assign LEDR[17:2] = bus.araddr[15:0];
   assign LEDG[1] = bus.arvalid;
   assign LEDG[0] = bus.arready;

   assign LEDG[7] = bus.rvalid;
   assign LEDG[6] = bus.rready;
	
	always_comb begin
		case(sel)
			2'd0: begin
				en_read = 0;
				en_init = 0;
				inconv0 = 4'h8;
				inconv1 = 4'h8;
				inconv2 = 4'hf;
				inconv3 = 4'h0;
				inconv4 = 4'hf;
				inconv5 = 4'h0;
				inconv6 = 4'hc;
				inconv7 = 4'ha;
				LEDR[17:15] = '0 ;
				LEDR[15:2] = '0 ;
			end
			
			2'd1: begin			//spi_init
				en_read = 0;
				en_init = 1;
				inconv0 = regsta1[3:0];
				inconv1 = regsta1[7:4];
				inconv2 = 4'hf;
				inconv3 = 4'h0;
				inconv4 = 4'hf;
				inconv5 = 4'h0;
				inconv6 = 4'hc;
				inconv7 = 4'ha;
				LEDR[17:15] = out_conflito ;
				LEDR[15:2] = '0 ;
			end
			2'd2: begin			//spi_read
				en_read = 1;
				en_init = 0;
				inconv0 = bus.rdata[3:0];
				inconv1 = bus.rdata[7:4];
				inconv2 = bus.rdata[11:8];
				inconv3 = bus.rdata[15:12];
				inconv4 = bus.rdata[19:16];
				inconv5 = bus.rdata[23:20];
				inconv6 = bus.rdata[27:24];
				inconv7 = bus.rdata[31:28];
				LEDR[17:2] = bus.araddr[15:0];
			end
			
			default: begin
				en_read = 0;
				en_init = 0;
				inconv0 = 4'h8;
				inconv1 = 4'h8;
				inconv2 = 4'hf;
				inconv3 = 4'h0;
				inconv4 = 4'hf;
				inconv5 = 4'h0;
				inconv6 = 4'hc;
				inconv7 = 4'ha;
				LEDR[17:2] = '1;
			end
		endcase
	end
*/
endmodule
