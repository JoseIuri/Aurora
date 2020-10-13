/// Esse módulo foi criado para simular a memória. Também faz uso da interface amba,
/// para fazer verificações de handshake para as transições de estados e "colocar"
/// o endereço (busmem.araddr) na variável address para ser possível buscar na memóra
/// "mem" carregada o dado correspondente ao endereço.
/// Também usa a entradas e saídas IO0, IO1, IO2 e IO3 no "sentido inverso" que o módulo
/// spi.sv. Já que esse módulo deve receber um endereço e retornar um dado.
/// Para acompanhar a máquina de estados de spi.sv usa-se também CS, CLOCK, VCC e GND,
/// sinais do módulo spi.sv que devem entrar na memória do CHIP.

module mem /* #(DATA_SIZE = 32)*/(
	axi4_lite_if busmem,
	inout IO0, IO1, IO2, IO3,
	input logic CS, CLOCK
);

	import axi4_types::*;

	localparam int BUSMEM_ADDR_SIZE = $bits(busmem.araddr);
	localparam int BUSMEM_DATA_SIZE = $bits(busmem.rdata);

	logic [31:0]mem[0:1023];

	initial begin
		$readmemh("dataMemo.txt", mem);
	end

	//logic in_out0, in_out1, in_out2, in_out3;
	logic [3:0] in_out;
	
	assign IO0 = in_out[0];
	assign IO1 = in_out[1];
	assign IO2 = in_out[2];
	assign IO3 = in_out[3];

	logic [3:0] count;
	logic [7:0] instruction;

	logic [7:0] m; 
	logic [BUSMEM_ADDR_SIZE-1:0] address;
	logic [BUSMEM_DATA_SIZE-1:0] memoria;

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

			count <= 4'h7;
			CURRENTSTATE <= WAIT_ADDR;

		end else begin

			CURRENTSTATE <= NEXTSTATE;

			case (CURRENTSTATE)
				FAST_READ_QIO: begin
					if (CLOCK==1) begin
						if(count<=4'd8) begin
							count <= count-1;
						end
					
						if(count==4'h0) begin
							count <= 4'd7;
						end	
					end
				end

				SEND_ADDR: begin 
					if(count==4'd0 && CLOCK ==1) begin
						count <= 4'd3;
						//busmem.rvalid <= 1;
					end else if(count<=4'd7 && CLOCK ==1) begin
						count <= count-1'b1;
					end

					unique case (count)
						4'd0: begin 
							m[3:0] = {IO3, IO2, IO1, IO0};
						end
						4'd1: begin
							m[7:4] =  {IO3, IO2, IO1, IO0};
						end
						4'd2,4'd3,4'd4, 4'd5, 4'd6, 4'd7: begin
							address[BUSMEM_ADDR_SIZE-4*(8-count) +:4] <= {IO3, IO2, IO1, IO0};//{IO3,IO2,IO1,IO0};
						end
					endcase

				end 

				DUMMY: begin
					if (CLOCK==1) begin
						if(count<=4'd3) begin
							count <= count-1'b1;
						end
						if(count==4'd0) begin
							count <= 7;
							memoria <= mem[address];
						end	
					end	
					
				end

				READ_DATA: begin 
					if(CLOCK==1) begin
						if(count<=4'd7) begin
							count <= count-1;
						end
						if(count==4'd0) begin
							count <= 4'd7;
						end	
					end
				end	
			endcase
		end
	end
				

	always_comb begin 

		in_out = 4'hz;
		NEXTSTATE = CURRENTSTATE;

		case (CURRENTSTATE)

			WAIT_ADDR: begin
				if (busmem.arready && busmem.arvalid) begin
					NEXTSTATE = FAST_READ_QIO;
				end 
			end
	
			FAST_READ_QIO: begin
				if(count==4'd0 && CLOCK==1) begin
					instruction[count] = IO0;
					NEXTSTATE = SEND_ADDR;
				end else if(count <=4'd7) begin
					instruction[count] = IO0;
					NEXTSTATE = FAST_READ_QIO;
				end
			end


			SEND_ADDR: begin
				if(count==4'd0) begin
					if(CLOCK==1) begin 
						NEXTSTATE = DUMMY; 
					end
				end else if(count<=4'd7) begin
					NEXTSTATE = SEND_ADDR;
				end
			end

			DUMMY: begin
				if(count<=4'd3) begin
					NEXTSTATE = DUMMY;
				end
				if(count==4'd0 && CLOCK==1) begin
					NEXTSTATE = READ_DATA;
				end
			end

			READ_DATA: begin
				
				unique case (count)
					4'd7,4'd6,4'd5,4'd4,4'd3,4'd2,4'd1,4'd0: begin
						{in_out[3],in_out[2],in_out[1],in_out[0]} = memoria[BUSMEM_DATA_SIZE-4*(8-count) +: 4];
						NEXTSTATE = READ_DATA;
						if(CLOCK==1 && count==0) begin
							NEXTSTATE = WAIT_RESP;
						end
					end
				endcase
			end

			WAIT_RESP: begin
				if(busmem.rvalid && busmem.rready) begin
					NEXTSTATE = WAIT_ADDR;
				end else if (!busmem.rready) begin
					NEXTSTATE = WAIT_RESP;
				end
			end

			WAIT: begin
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