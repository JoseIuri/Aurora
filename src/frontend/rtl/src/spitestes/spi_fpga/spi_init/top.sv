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
				GPIO_1,							//	GPIO Connection 0 I/O
				GPIO_CLKIN_N1,     			//	GPIO Connection 0 Clock Input 0
				GPIO_CLKIN_P1,          	//	GPIO Connection 0 Clock Input 1
				//GPIO_CLKOUT_N0,     			//	GPIO Connection 0 Clock Output 0
				//GPIO_CLKOUT_P0, 	
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
logic countcoco;
logic [7:0]regsta1;

logic CLK;
inout	[35:0]	GPIO_1;					//	GPIO Connection 0 I/O
input	logic	GPIO_CLKIN_N1;     		//	GPIO Connection 0 Clock Input 0
input	logic GPIO_CLKIN_P1;          //	GPIO Connection 0 Clock Input 1
//inout			GPIO_CLKOUT_N0;     	//	GPIO Connection 0 Clock Output 0
//inout			GPIO_CLKOUT_P0;         //	GPIO Connection 0 Clock Output 1

	div_freq clk_1 (.ARESETn(SW[0]), .ACLK(CLOCK_50), .clk_1(CLK));
	axi4_lite_if #(.ADDR_SIZE(24)) bus(.ACLK(CLK),.ARESETn(SW[0]));
	spi_init teste (.busmem(bus), .IO0(GPIO_1[22]), .IO1(GPIO_1[30]), .IO2(GPIO_1[32]), .IO3(GPIO_1[26]), .CS(GPIO_1[28]), .CLOCK(GPIO_1[24]), .flag_end_init(LEDG[8]), .estado(LEDR[17:15]), .status_reg_lido(regsta1));
	assign LEDG[0] = CLK;
	
	assign GPIO_1[23] = 1'b0;
	assign GPIO_1[25] = 1'b0;
	assign GPIO_1[27] = 1'b0;
	assign GPIO_1[29] = 1'b0;
	assign GPIO_1[31] = 1'b0;
	assign GPIO_1[33] = 1'b0;

	Conv_Hexa_7seg CONV0(.Entrada(regsta1[3:0]),   .Saida(HEX0)),
				      CONV1(.Entrada(regsta1[7:4]),   .Saida(HEX1));

endmodule