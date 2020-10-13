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
	//localparam int BUSMEM_ADDR_SIZE = busmem.ADDR_SIZE;
	localparam int BUSMEM_ADDR_SIZE = $bits(busmem.araddr);
	localparam int BUSMEM_DATA_SIZE = $bits(busmem.rdata);

	logic [3:0] in_out;
	
	assign IO0 = in_out[0];
	assign IO1 = in_out[1];
	assign IO2 = in_out[2];
	assign IO3 = in_out[3];

	logic [3:0] count;
	logic [7:0] instruction;

	logic [BUSMEM_ADDR_SIZE-1:0] address;

	typedef enum logic[2:0]{
		WAIT_ADDR,
		FAST_READ_QIO,
		SEND_ADDR,
		DUMMY,
		READ_DATA,
		WAIT_RESP,
		WAIT
	} state;

	state CURRENTSTATE;
	state NEXTSTATE;

	//Using the IC W25Q64CV
	//with Quad SPI Instructions

	// IO0 -> DI
	// IO1 -> DO
	// IO2 -> /WP
	// IO3 -> /HOLD

	//Fast Read Quad I/O (instruction: EBh)

	always_ff @(posedge busmem.ACLK) begin
		if(!busmem.ARESETn) begin

			count <= 5'd7;
			CLOCK <= 0;
			CURRENTSTATE <= WAIT_ADDR;
		
			//Read Address Channel
			//recebe .arvalid e .araddr
			busmem.arready <= 0;
			//Read Data Channel
			busmem.rvalid <= 0;
			busmem.rdata <= 0;
			busmem.rresp <= AXI4_RESP_L_OKAY;
		
			address <= '0;
			instruction <= 8'h00;
			

		end else begin
			
			CLOCK <= ~CLOCK;
			CURRENTSTATE <= NEXTSTATE;

			unique case (CURRENTSTATE)
				WAIT_ADDR: begin
					busmem.arready <= 1;
					busmem.rdata <= 32'hBABABABE;
					if (busmem.arready && busmem.arvalid) begin
						address <= busmem.araddr;
						instruction <= 8'hEB;
					end
				end			

				FAST_READ_QIO: begin
					if (CLOCK==1) begin
						if(count<=5'd8) begin
							count <= count-1;
						end
						if(count==5'h00) begin
							count <= 5'd7;
						end	
					end
				end
				SEND_ADDR: begin 
					if(CLOCK==1) begin
						if(count<=5'd7) begin
							count <= count-1;
						end
						if(count==5'd0) begin
							count <= 5'd3;
						end	
					end
				end

				DUMMY: begin
					if (CLOCK==1) begin
						if(count<=5'd3) begin
							count <= count-1;
						end
						if(count==5'd0) begin
							count <= 5'd7;
						end	
					end
					
				end
				READ_DATA: begin 
					if(count==5'd0 && CLOCK ==1) begin
						count <= 5'd7;
						busmem.rdata[BUSMEM_DATA_SIZE-4 * (8 - count) +: 4] <= {IO3,IO2,IO1,IO0};
						//busmem.rvalid <= 1;
					end else if(count<=5'd7 && CLOCK ==1) begin
						count <= count-1;
						busmem.rdata[BUSMEM_DATA_SIZE-4 * (8 - count) +: 4] <= {IO3,IO2,IO1,IO0};
					end
				end		
				WAIT_RESP: begin
					busmem.rvalid <= 1;
					busmem.arready <= 0;
					if(busmem.rvalid && busmem.rready) begin
						busmem.rvalid <= 0;
						busmem.rresp <= AXI4_RESP_L_OKAY;
					end else if (!busmem.rready) begin
						busmem.rvalid <= 1;
					end
				end
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
				end else if(count <=5'd7) begin
					in_out[0] =  instruction[count];
					NEXTSTATE = FAST_READ_QIO;
				end

			end

			SEND_ADDR: begin
				// Memória de Instrução do Pulpino: Inicia em 0x0000 0000 e termina em 0x0000 8000- 1000 0000 0000 0000
				unique case (count)
					5, 6, 7: begin
						in_out = 4'b0000;
						NEXTSTATE = SEND_ADDR;
					end
					4,3,2: begin
						in_out[3:0] = address[(BUSMEM_ADDR_SIZE-4*(5-count)) +: 4];
						NEXTSTATE = SEND_ADDR;
					end
					0, 1: begin //ESSES SÃO AQUELES M
						in_out = 4'b0000;
						NEXTSTATE = (count==0 && CLOCK==1) ? DUMMY : SEND_ADDR;
					end
				endcase
			end

			DUMMY: begin
				if(count==0 && CLOCK==1) begin
					NEXTSTATE = READ_DATA;
				end else if(count<=3) begin
					NEXTSTATE = DUMMY;
				end
			end


			READ_DATA: begin
				if(count==0) begin
					if(CLOCK==1) begin 
						NEXTSTATE = WAIT_RESP; 
					end
				end else if(count<=7) begin
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
			end
		endcase
	end
endmodule