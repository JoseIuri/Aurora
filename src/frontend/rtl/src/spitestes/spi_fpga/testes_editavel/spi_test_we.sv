/////////////// LER README.txt PARA ENTENDER O FUNCIONAMENTO

module spi_test_we (
	axi4_lite_if busmem,
	inout IO0, IO1, IO2, IO3,
	output logic CS, CLOCK, flag_end,
	output logic [7:0] status_reg_lido1, status_reg_lido2
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
	logic flag_inst;
	logic [BUSMEM_ADDR_SIZE-1:0] address;

typedef enum logic[2:0]{
		WRITE_EN,
		INSTRU_READ_SR,
		READ_SR,
		IDLE
	} state;

	state CURRENTSTATE;
	state NEXTSTATE;
	assign estado = CURRENTSTATE;
	
	always_ff @(posedge busmem.ACLK) begin
		if(!busmem.ARESETn) begin
			count <= 4'd7;
			instruction <= 8'h00;
			status_reg_lido1 <= 8'h00;
			status_reg_lido2 <= 8'h00;
			flag_end <= 0;
			flag_inst <= 0;
			CLOCK <= 0;
			CURRENTSTATE <= IDLE;

		end else begin
			if(CS == 0) begin
				CLOCK <= ~CLOCK;
			end else begin
				CLOCK <= 0;
			end

			CURRENTSTATE <= NEXTSTATE;

			unique case (CURRENTSTATE)
				WRITE_EN: begin
					if(count == 4'hF) begin
						count <= 4'd7; 
						instruction <= 8'h05; 
					end else if(CLOCK == 1) begin
						count <= count-1;
					end
				end

				INSTRU_READ_SR: begin
					if(CLOCK == 1 && count<=4'd7) begin
						count <= count-1;
						if(count==4'h0) begin
							count <= 4'd7;
						end
					end
				end

				READ_SR: begin
					if(count==0 && CLOCK ==1) begin
						if(IO1==0) begin
							if(flag_inst==0) begin
								flag_inst<=1;
							end else if(flag_inst) begin
								flag_end <= 1'b1;
							end
						end
						if (flag_inst==0) begin
							status_reg_lido1[count] <= IO1;
						end else if (flag_inst) begin
							status_reg_lido2[count] <= IO1;
						end
						count <= 4'd7;
					end else if(count<=4'd7 && CLOCK ==1) begin
						if (flag_inst==0) begin
							status_reg_lido1[count] <= IO1;
						end else if (flag_inst) begin
							status_reg_lido2[count] <= IO1;
						end
						count <= count-1;
					end
				end

				IDLE: begin
					if(!flag_inst) begin
						instruction <= 8'h05;
					end else begin
						instruction <= 8'h06;
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
			WRITE_EN: begin
				unique case (count)
					4'd7,4'd6,4'd5,4'd4,4'd3,4'd2,4'd1,4'd0: begin
						CS = 1'b0;
						in_out[0] = instruction[count];
						NEXTSTATE = WRITE_EN;
					end
					4'hF: begin
						CS = 1'b1;
						NEXTSTATE = INSTRU_READ_SR;
					end
				endcase
			end

			INSTRU_READ_SR: begin
				unique case (count)
					4'd7,4'd6,4'd5,4'd4,4'd3,4'd2,4'd1: begin
						CS = 1'b0;
						in_out[0] = instruction[count];
						NEXTSTATE = INSTRU_READ_SR;
					end
					4'h0: begin
						CS = 1'b0;
						in_out[0] = instruction[count];
						if(CLOCK==1) begin
							NEXTSTATE = READ_SR;
						end
					end
				endcase
			end

			READ_SR: begin
				if(count==0) begin
					if(IO1==0) begin
						if(CLOCK==1) begin
							NEXTSTATE = IDLE; 
						end
					end else begin
						NEXTSTATE = READ_SR;
					end
				end		
			end

			IDLE: begin
				CS = 1'b1;
				if (flag_end) begin
					NEXTSTATE = IDLE;
				end else if(busmem.ARESETn) begin
					if (flag_inst) begin
						NEXTSTATE=WRITE_EN;
					end else if (!flag_inst) begin
						NEXTSTATE=INSTRU_READ_SR;
					end
				end
			end
		endcase
	end
endmodule
