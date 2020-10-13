/// Esse módulo deve se comunicar com o chip de memória 25Q32BVA1G (winbond).
/// Utiliza os sinais IO0, IO1, IO2 e IO3 para entrada e saída de dados e os
/// sinais CS, CLOCK, VCC e GND para serem os respectivos sinais de entrada
/// no chip. Antes de utilizar esse módulo, faz-se necessário realizar a rotina
/// de spi_init.sv, para habilitar enviar a instrução EBh relativa a instrução
/// do modo de Fast Read Quad I/O.

module spi (
	axi4_lite_if busmem,
	inout IO0, IO1, IO2, IO3,
	output logic CS, CLOCK
);

	import axi4_types::*;

	localparam int BUSMEM_ADDR_SIZE = busmem.ADDR_SIZE;
	//localparam int BUSMEM_ADDR_SIZE = $bits(busmem.araddr);
	localparam int BUSMEM_DATA_SIZE = busmem.DATA_SIZE;

	logic [3:0] in_out;
	
	assign IO0 = in_out[0];
	assign IO1 = in_out[1];
	assign IO2 = in_out[2];
	assign IO3 = in_out[3];

	logic [3:0] count;
	logic [7:0] instruction;

	typedef enum logic[2:0]{
		WAIT_ADDR,
		FAST_READ_QIO,
		SEND_ADDR,
		DUMMY,
		READ_DATA,
		WAIT_RESP,
		WAIT
	} state;

	state NEXTSTATE;
	state CURRENTSTATE;

	//Using the IC W25Q64CV
	//with Quad SPI Instructions

	// IO0 -> DI
	// IO1 -> DO
	// IO2 -> /WP
	// IO3 -> /HOLD

	//Fast Read Quad I/O (instruction: EBh)

	always_ff @(posedge busmem.ACLK) begin
		if(!busmem.ARESETn) begin

			count <= 4'd7;
			CLOCK <= 0;
			CURRENTSTATE <= WAIT_ADDR;

			//Read Address Channel
			//recebe .arvalid e .araddr
			busmem.arready <= 0;
			//Read Data Channel
			busmem.rvalid <= 0;
			busmem.rdata <= 0;
			busmem.rresp <= AXI4_RESP_L_SLVERR;

			instruction <= 8'h00;

		end else begin

			if(CS == 0) begin
				CLOCK <= ~CLOCK;
			end else begin
				CLOCK <= 0;
			end

			CURRENTSTATE <= NEXTSTATE;

			unique case (CURRENTSTATE)
				WAIT_ADDR: begin
					busmem.arready <= 1;
					if (busmem.arready && busmem.arvalid) begin
						busmem.arready <= 0;
						instruction <= 8'hEB;
					end 
				end

				FAST_READ_QIO: begin
					if(count<=4'd7 && CLOCK ==1) begin
						count <= count-1;
						if(count==4'd0) begin
							count <= 4'd7;
						end
					end
				end

				SEND_ADDR: begin 
					if(count<=4'd7 && CLOCK ==1) begin
						count <= count-1;
						if(count==4'd0) begin
							count <= 4'd3;
						end
					end
				end

				DUMMY: begin
					if(count<=4'd3 && CLOCK ==1) begin
						count <= count-1;
						if(count==4'd0) begin
							count <= 4'd7;
						end
					end
				end

				READ_DATA: begin 
					if(count<=4'd7 && CLOCK ==1) begin
						count <= count-1;
						busmem.rdata[BUSMEM_DATA_SIZE-4 * (8 - count) +: 4] <= {IO3,IO2,IO1,IO0};
						if(count==4'd0) begin
							count <= 4'd7;
							busmem.rresp <= AXI4_RESP_L_OKAY;
							busmem.rvalid <= 1;
							busmem.rdata[BUSMEM_DATA_SIZE-4 * (8 - count) +: 4] <= {IO3,IO2,IO1,IO0};
						end
					end
				end	

				WAIT_RESP: begin
					//busmem.rvalid <= 1;
					//busmem.arready <= 0;
					if(busmem.rvalid && busmem.rready) begin
						busmem.rvalid <= 0;
						busmem.arready <= 1;
						//busmem.rresp <= AXI4_RESP_L_OKAY;
						//$display("SLAVE  %0d dado: %h, memoriatxt: %h",busmem.araddr[9:0]+1'd1,busmem.rdata, mem[address]);
						//$display("rresp: %s", busmem.rresp);
					end else if (!busmem.rready) begin
						busmem.rvalid <= 1;
					end
				end

				/*WAIT: begin
					count <=7;
					if(count<=7) begin
						count <= count-1;
					end
					if(count==0) begin
						count <= 23;
					end	
				end*/
			endcase
		end
	end
				

	always_comb begin 

		in_out = 4'hz;
		CS = 1'b0;
		NEXTSTATE = CURRENTSTATE;

		unique case (CURRENTSTATE)

			WAIT_ADDR: begin
				CS = 1'b1;
				if (busmem.arready && busmem.arvalid) begin
					NEXTSTATE = FAST_READ_QIO;
				end 
			end
			
			FAST_READ_QIO: begin
				if(count==0 && CLOCK==1) begin
					in_out[0] = instruction[count];
					NEXTSTATE = SEND_ADDR;
				end else if(count <=4'd7) begin
					in_out[0] =  instruction[count];
					NEXTSTATE = FAST_READ_QIO;
				end

			end

			SEND_ADDR: begin
				// Memória de Instrução do Pulpino: Inicia em 0x0000 0000 e termina em 0x0000 8000- 1000 0000 0000 0000
				unique case (count)
					4'd4,4'd3,4'd2, 4'd5, 4'd6, 4'd7: begin
						in_out[3:0] = busmem.araddr[(BUSMEM_ADDR_SIZE-4*(8-count)) +: 4];//address
						NEXTSTATE = SEND_ADDR;
					end
					4'd0, 4'd1: begin //ESSES SÃO AQUELES M
						in_out = 4'b0000;
						NEXTSTATE = (count==0 && CLOCK==1) ? DUMMY : SEND_ADDR;
					end
				endcase
			end

			DUMMY: begin
				if(count<=4'd3) begin
					NEXTSTATE = DUMMY;
				end
				if(count==0 && CLOCK==1) begin
					NEXTSTATE = READ_DATA;
				end
			end


			READ_DATA: begin

			//busmem.rdata[busmem.DATA_SIZE-1:busmem.DATA_SIZE-4] = {IO3,IO2,IO1,IO0};
			//busmem.rdata[busmem.DATA_SIZE-4 +: 4] = {IO3,IO2,IO1,IO0};
			//busmem.rdata[busmem.DATA_SIZE-4 * (8 - count) +: 4] = {IO3,IO2,IO1,IO0};
				if(count==0) begin
					if(CLOCK==1) begin 
						NEXTSTATE = WAIT_RESP; 
					end
				end else if(count<=4'd7) begin
					NEXTSTATE = READ_DATA;
				end
			end

			WAIT_RESP: begin
				CS =1'b1;

				if(busmem.rvalid && busmem.rready) begin
					NEXTSTATE = WAIT_ADDR;
				end
			end

			WAIT: begin
				CS = 1'b1;
				if(busmem.ARESETn) begin
					NEXTSTATE=WAIT_ADDR;
				end 
				/*if(busmem.arvalid) begin
					NEXTSTATE = SEND_ADDR;
				end*/
			end

		endcase
	end
endmodule