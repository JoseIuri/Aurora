module spi (
	axi4_lite_if busmem,
	inout IO0, IO1, IO2, IO3,
	output logic CS, CLOCK,
	output logic [2:0]estados
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

	logic [4:0] count;
	logic [7:0] instruction;

	typedef enum logic[2:0]{
		WAIT_ADDR,
		INSTR_READ_SPI,
		SEND_ADDR,
		READ_DATA,
		WAIT_RESP,
		IDLE
	} state;

	state CURRENTSTATE;
	state NEXTSTATE;
	assign estados = CURRENTSTATE;
	//Using the IC W25Q64CV
	//with SPI (instruction: 03h)

	always_ff @(posedge busmem.ACLK) begin
		if(!busmem.ARESETn) begin

			count <= 5'd7;
			CLOCK <= 0;
			CURRENTSTATE <= IDLE;
		
			//Read Address Channel
			//recebe .arvalid e .araddr
			busmem.arready <= 0;
			//Read Data Channel
			busmem.rvalid <= 0;
			busmem.rdata <= 0;
			busmem.rresp <= AXI4_RESP_L_OKAY;

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
					busmem.rdata <= 32'hBABABABE;
					if (busmem.arready && busmem.arvalid) begin
						instruction <= 8'h03;
					end
				end			

				INSTR_READ_SPI: begin
					if(count<=5'd7 && CLOCK ==1) begin
						count <= count-1'b1;
						if(count==5'd0) begin
							count <= 5'd23;
						end
					end
				end

				SEND_ADDR: begin 
					if(count<=5'd23 && CLOCK ==1) begin
						count <= count-1'b1;
						if(count==5'd0) begin
							count <= 5'd31;
						end
					end
				end

				READ_DATA: begin 
					if(count<=5'd31 && CLOCK ==1) begin
						count <= count-1'b1;
						busmem.rdata[BUSMEM_DATA_SIZE-(32 - count)] <= IO1;
						if(count==5'd0) begin
							count <= 5'd7;
							busmem.rresp <= AXI4_RESP_L_OKAY;
							busmem.rdata[BUSMEM_DATA_SIZE-(32 - count)] <= IO1;
						end
					end
				end	

				WAIT_RESP: begin
					busmem.rvalid <= 1;
					busmem.arready <= 0;
					if(busmem.rvalid && busmem.rready) begin
						busmem.rvalid <= 0;
					end else if (!busmem.rready) begin
						busmem.rvalid <= 1;
					end
				end
			endcase
		end
	end

	always_comb begin 

		in_out[1:0] = 2'hz;
		in_out[2] = 1'b1;
		in_out[3] = 1'b1;
		CS = 1'b0;
		NEXTSTATE = CURRENTSTATE;

		unique case (CURRENTSTATE)

			WAIT_ADDR: begin
				CS = 1'b1;
				if (busmem.arready && busmem.arvalid) begin
					NEXTSTATE = INSTR_READ_SPI;
				end 
			end
			
			INSTR_READ_SPI: begin
				if(count==5'd0 && CLOCK==1) begin
					in_out[0] = instruction[count];
					NEXTSTATE = SEND_ADDR;
				end else if(count <=5'd7) begin
					in_out[0] =  instruction[count];
					NEXTSTATE = INSTR_READ_SPI;
				end

			end

			SEND_ADDR: begin
				/*if(count <=5'd23) begin
					in_out[0] = busmem.araddr[BUSMEM_ADDR_SIZE-(24-count)];
					NEXTSTATE = SEND_ADDR;
				end else if(count ==5'd0 && CLOCK==1) begin
					in_out[0] =  busmem.araddr[BUSMEM_ADDR_SIZE-(24-count)];
				if() begin
						NEXTSTATE = READ_DATA;
					end
				end*/
				if(count==5'd0 && CLOCK==1) begin
					in_out[0] = busmem.araddr[BUSMEM_ADDR_SIZE-(24-count)];
					NEXTSTATE = READ_DATA;
				end else if(count <=5'd23) begin
					in_out[0] =  busmem.araddr[BUSMEM_ADDR_SIZE-(24-count)];
					NEXTSTATE = SEND_ADDR;
				end
			end
			
			READ_DATA: begin
				if(count==5'd0) begin
					if(CLOCK==1) begin 
						NEXTSTATE = WAIT_RESP; 
					end
				end else if(count<=5'd31) begin
					NEXTSTATE = READ_DATA;
				end
			end

			WAIT_RESP: begin
				CS =1'b1;
				if(busmem.rvalid && busmem.rready) begin
					NEXTSTATE = WAIT_ADDR;
				end
			end
			
			IDLE: begin
				CS = 1'b1;
				if(busmem.ARESETn) begin
					NEXTSTATE=WAIT_ADDR;
				end 
			end
		endcase
	end
endmodule