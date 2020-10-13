module top(	CLOCK_27, 
			CLOCK_50, 
			KEY, 
			SW, 
			HEX0, 
			HEX1, 
			HEX2, 
			HEX3, 
			HEX4, 
			HEX5, 
			HEX6, 
			HEX7, 
			GPIO_1,						//	GPIO Connection 0 I/O
			GPIO_CLKIN_N1,     			//	GPIO Connection 0 Clock Input 0
			GPIO_CLKIN_P1,          	//	GPIO Connection 0 Clock Input 1
			GPIO_CLKOUT_N1,     		//	GPIO Connection 0 Clock Output 0
			GPIO_CLKOUT_P1, 	
			LEDG, 
			LEDR);

input logic CLOCK_27;
input logic CLOCK_50;

input logic [3:0] KEY;
input logic [17:0] SW;

output logic [6:0] HEX0;
output logic [6:0] HEX1;
output logic [6:0] HEX2;
output logic [6:0] HEX3;
output logic [6:0] HEX4;
output logic [6:0] HEX5;
output logic [6:0] HEX6;
output logic [6:0] HEX7;

output logic [8:0] LEDG;
output logic [17:0] LEDR;

inout	[35:0]	GPIO_1;					//	GPIO Connection 0 I/O
input	logic	GPIO_CLKIN_N1;     		//	GPIO Connection 0 Clock Input 0
input	logic	GPIO_CLKIN_P1;          //	GPIO Connection 0 Clock Input 1
inout			GPIO_CLKOUT_N1;     	//	GPIO Connection 0 Clock Output 0
inout			GPIO_CLKOUT_P1;         //	GPIO Connection 0 Clock Output 1

	div_freq clk_1 (.ARESETn(SW[0]), .ACLK(CLOCK_50), .clk_1(CLK));
	axi4_lite_if #(.ADDR_SIZE(24), .DATA_SIZE(32)) bus(.ACLK(CLK),.ARESETn(SW[0]));
	master_spi teste_master (.master(bus));
	spi teste (.busmem(bus), .IO0(GPIO_1[22]), .IO1(GPIO_1[30]), .IO2(GPIO_1[32]), .IO3(GPIO_1[26]), .CS(GPIO_1[28]), .CLOCK(GPIO_1[24]), .estados(LEDR[17:15]));
	
	assign GPIO_1[23] = 1'b0;
	assign GPIO_1[25] = 1'b0;
	assign GPIO_1[27] = 1'b0;
	assign GPIO_1[29] = 1'b0;
	assign GPIO_1[31] = 1'b0;
	assign GPIO_1[33] = 1'b0;	
		
	assign LEDG[8] = CLK;
	assign LEDG[1] = bus.arvalid;
	assign LEDG[0] = bus.arready;

	assign LEDG[7] = bus.rvalid;
	assign LEDG[6] = bus.rready;
		

	Conv_Hexa_7seg CONV0(.Entrada(bus.rdata[3:0]),   .Saida(HEX0)),
				   CONV1(.Entrada(bus.rdata[7:4]),   .Saida(HEX1)),
				   CONV2(.Entrada(bus.rdata[11:8]),  .Saida(HEX2)),
				   CONV3(.Entrada(bus.rdata[15:12]), .Saida(HEX3)),
				   CONV4(.Entrada(bus.rdata[19:16]), .Saida(HEX4)),
				   CONV5(.Entrada(bus.rdata[23:20]), .Saida(HEX5)),
				   CONV6(.Entrada(bus.rdata[27:24]), .Saida(HEX6)),
				   CONV7(.Entrada(bus.rdata[31:28]), .Saida(HEX7));	

endmodule