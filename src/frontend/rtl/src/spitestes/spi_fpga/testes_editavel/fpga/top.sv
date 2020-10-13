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
logic flagend;
//output logic [35:0]GPIO_1;
logic [7:0]regsta1, regsta2;
logic [2:0] conte;
wire fio1,fio2,fio3,fio4,fio5,fio6;

logic CLK;
inout	[35:0]	GPIO_1;					//	GPIO Connection 0 I/O
input	logic	GPIO_CLKIN_N1;     		//	GPIO Connection 0 Clock Input 0
input	logic GPIO_CLKIN_P1;          //	GPIO Connection 0 Clock Input 1
//inout			GPIO_CLKOUT_N0;     	//	GPIO Connection 0 Clock Output 0
//inout			GPIO_CLKOUT_P0;         //	GPIO Connection 0 Clock Output 1

	div_freq clk_1 (.ARESETn(SW[0]), .ACLK(CLOCK_50), .clk_1(CLK));
	axi4_lite_if #(.ADDR_SIZE(24)) bus(.ACLK(CLK),.ARESETn(SW[0]));
	spi teste (.busmem(bus), .IO0(GPIO_1[22]), .IO1(GPIO_1[30]), .IO2(GPIO_1[32]), .IO3(GPIO_1[26]), .CS(GPIO_1[28]), .CLOCK(GPIO_1[24]), .flag_end(flagend), .estado(LEDR[17:15]), .contador(conte), .status_reg_lido1(regsta1), .status_reg_lido2(regsta2));
	//spi teste (.busmem(bus), .IO0(fio1), .IO1(fio2), .IO2(fio3), .IO3(fio4), .CS(fio5), .CLOCK(fio6), .flag_end(flagend), .estado(LEDR[17:15]), .status_reg_lido1(regsta1), .status_reg_lido2(regsta2));
	//mem teste_mem (.busmem(bus), .IO0(GPIO_1[20]), .IO1(GPIO_1[24]), .IO2(GPIO_1[25]), .IO3(GPIO_1[22]), .CS(GPIO_1[23]), .CLOCK(GPIO_1[21]), .flag_end(flagend));
	assign LEDG[0] = CLK;
	assign LEDG[8] = flagend;
		
	assign GPIO_1[23] = 1'b0;
	assign GPIO_1[25] = 1'b0;
	assign GPIO_1[27] = 1'b0;
	assign GPIO_1[29] = 1'b0;
	assign GPIO_1[31] = 1'b0;
	assign GPIO_1[33] = 1'b0;	
	
	Conv_Hexa_7seg CONV0(.Entrada(regsta1[3:0]),   .Saida(HEX0)),
				      CONV1(.Entrada(regsta1[7:4]),   .Saida(HEX1)),
				      CONV2(.Entrada(regsta2[3:0]),   .Saida(HEX2)),
				      CONV3(.Entrada(regsta2[7:4]),   .Saida(HEX3)),
						
//				      CONV4(.Entrada(conte[3:0]),   .Saida(HEX6)),
						CONV5(.Entrada(conte[2:0]),   .Saida(HEX7));

endmodule