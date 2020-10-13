module juntatudo(     	input wire CLOCK_27,
                        input wire CLOCK_50,
                        input wire [3:0] KEY,
                        input wire [17:0] SW,
                        output wire [6:0] HEX0,
                        output wire [6:0]HEX1,
                        output wire [6:0]HEX2,
                        output wire [6:0]HEX3,
                        output wire [6:0]HEX4,
                        output wire [6:0]HEX5,
                        output wire [6:0]HEX6,
                        output wire [6:0]HEX7,
                        inout wire [31:0]GPIO_1,                                         //      GPIO Connection 0 I/O
                        input wire GPIO_CLKIN_N1,                          //      GPIO Connection 0 Clock Input 0
                        input wire GPIO_CLKIN_P1,                  //      GPIO Connection 0 Clock Input 1
                        inout GPIO_CLKOUT_N1,                 //      GPIO Connection 0 Clock Output 0
                        inout GPIO_CLKOUT_P1,
                        output wire [8:0] LEDG,
                        output wire [17:0] LEDR
);
	
	logic [7:0]regsta1;
	logic [3:0] inconv0, inconv1, inconv2, inconv3, inconv4, inconv5, inconv6, inconv7;
	div_freq clk_1 (.ARESETn(SW[0]), .ACLK(CLOCK_50), .clk_1(CLK));
   axi4_lite_if #(.ADDR_SIZE(24)) bus(.ACLK(CLK),.ARESETn(SW[0]));
   //master_spi teste_master (.master(bus));
   //spi teste (.busmem(bus), .IO0(GPIO_1[20]), .IO1(GPIO_1[24]), .IO2(GPIO_1[25]), .IO3(GPIO_1[22]), .CS(GPIO_1[23]), .CLOCK(GPIO_1[21]));
	/*
	wire en_read, en_init;
	
	spi_read read_module(
	.rti(bus),
	.IO0(GPIO_1[20]),
	.IO1(GPIO_1[24]),
	.IO2(GPIO_1[25]),
	.IO3(GPIO_1[22]),
	.enable(en_read),
	.CS(GPIO_1[23]),
	.spi_clk(GPIO_1[21])
	);
								
	spi_init init_module(
	.busmem(bus),
	.IO0(GPIO_1[20]),
	.IO1(GPIO_1[24]),
	.IO2(GPIO_1[25]),
	.IO3(GPIO_1[22]),
	.enable(en_init),
	.CS(GPIO_1[23]), 
	.CLOCK(GPIO_1[21]), 
	.flag_end_init(LEDG[8]),
	.estado(out_conflito),
	.status_reg_lido(regsta1)
	);*/
	
top spi_module(
.bus(bus),
.IO0(GPIO_1[20]),
.IO1(GPIO_1[24]),
.IO2(GPIO_1[25]),
.IO3(GPIO_1[22]),
.CS(GPIO_1[23]),
.spi_clk(GPIO_1[21]),
.flag_end_init(out_conflito),
.en_read(en_read),
.en_init(en_init),
.init_state(out_conflito),
.regsta1(regsta1)
);
	
   assign LEDR[0] = CLK;
   //assign LEDR[17:2] = bus.araddr[15:0];
   assign LEDG[1] = bus.arvalid;
   assign LEDG[0] = bus.arready;

   assign LEDG[7] = bus.rvalid;
   assign LEDG[6] = bus.rready;
	
	always_comb begin
		case(SW[2:1])
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


   Conv_Hexa_7seg CONV0(.Entrada(inconv0),   .Saida(HEX0)),
                  CONV1(.Entrada(inconv1),   .Saida(HEX1)),
                  CONV2(.Entrada(inconv2),  .Saida(HEX2)),
                  CONV3(.Entrada(inconv3), .Saida(HEX3)),
                  CONV4(.Entrada(inconv4), .Saida(HEX4)),
                  CONV5(.Entrada(inconv5), .Saida(HEX5)),
                  CONV6(.Entrada(inconv6), .Saida(HEX6)),
                  CONV7(.Entrada(inconv7), .Saida(HEX7)
);
								
/*Conv_Hexa_7seg CONV0(.Entrada(bus.rdata[3:0]),   .Saida(HEX0)),
                        CONV1(.Entrada(bus.rdata[7:4]),   .Saida(HEX1)),
                        CONV2(.Entrada(bus.rdata[11:8]),  .Saida(HEX2)),
                        CONV3(.Entrada(bus.rdata[15:12]), .Saida(HEX3)),
                        CONV4(.Entrada(bus.rdata[19:16]), .Saida(HEX4)),
                        CONV5(.Entrada(bus.rdata[23:20]), .Saida(HEX5)),
                        CONV6(.Entrada(bus.rdata[27:24]), .Saida(HEX6)),
                        CONV7(.Entrada(bus.rdata[31:28]), .Saida(HEX7));
*/
								
/*Conv_Hexa_7seg CONV0(.Entrada(regsta1[3:0]),   .Saida(HEX0)),
                                      CONV1(.Entrada(regsta1[7:4]),   .Saida(HEX1));
*/





endmodule
