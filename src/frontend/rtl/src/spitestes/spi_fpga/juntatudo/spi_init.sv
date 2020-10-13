module spi_init  (
	axi4_lite_if busmem,
	inout IO0, IO1, IO2, IO3,
	input logic enable,
	output logic CS, CLOCK, flag_end_init,
	output logic [2:0]estado,
	output logic [7:0] status_reg_lido
);

	localparam int BUSMEM_ADDR_SIZE = $bits(busmem.ADDR_SIZE);
	localparam int BUSMEM_DATA_SIZE = $bits(busmem.DATA_SIZE);

	logic [3:0] in_out;
	
	assign IO0 = in_out[0];
	assign IO1 = in_out[1];
	assign IO2 = in_out[2];
	assign IO3 = in_out[3];

	logic [4:0] count; // Contador para enviar instruçoes e para escrever ou ler o registrador de status;	
	logic [7:0] instruction;
	logic flag_instr_wsr;
	
	logic [15:0] status_reg1_2;
	
	typedef enum logic[2:0]{
		WRITE_EN,
		WRITE_SR,
		INSTRU_READ_SR,
		READ_SR,
		IDLE
	} state;

	state NEXTSTATE;
	state CURRENTSTATE;
	assign estado = CURRENTSTATE;

	//Using the IC W25Q64CV
	//with Quad SPI Instructions

	always_ff @(posedge busmem.ACLK) begin
		if(!busmem.ARESETn) begin
			count <= 5'd7;
			flag_instr_wsr <= '0;
			status_reg1_2 <= '0;
			instruction <= 8'h00;
			flag_end_init <= 0;
			status_reg_lido <= 8'h00;
			CLOCK <= 0;
			CURRENTSTATE <= IDLE;

		end else begin
		  if(enable) begin
			if(CS == 0) begin
				CLOCK <= ~CLOCK;
			end else begin
				CLOCK <= 0;
			end

			CURRENTSTATE <= NEXTSTATE;

			unique case (CURRENTSTATE)

				WRITE_EN: begin
					//instruction <= 8'h06; vem do idle
					if(count == 5'h1F) begin
						count <= 5'd7; 
						status_reg1_2 <= 16'h0202;
						instruction <= 8'h01; 
					end else if(CLOCK == 1) begin
						count <= count-1;
					end
				end

				WRITE_SR: begin
					if(flag_instr_wsr && count==5'h1F) begin
						count <= 5'd7;
						instruction <= 8'h05; 
					end else if(CLOCK == 1) begin
						count <= count-1;
						if(flag_instr_wsr==0 && count==0) begin
							count <= 5'd15;
							flag_instr_wsr <=1;
						end
					end
				end

				INSTRU_READ_SR: begin
					if(CLOCK == 1 && count<=5'd7) begin
						count <= count-1;
						if(count==5'h00) begin
							count <= 5'd7;
						end
					end
				end

				READ_SR: begin
					if(count==0 && CLOCK ==1) begin
						if(IO1==0) begin
							flag_end_init <= 1'b1;
						end
						status_reg_lido[count] <= IO1;
						count <= 5'd7;
					end else if(count<=5'd7 && CLOCK ==1) begin
						status_reg_lido[count] <= IO1;
						count <= count-1;
					end
				end

				IDLE: begin
					instruction <= 8'h06;
				end
			endcase
		  end else begin
				CLOCK = 'z;
				flag_end_init = 'z;
				status_reg_lido = 'z;
		  end
		end
	end



	always_comb begin 
	  if(enable) begin
		in_out = 4'hz;
		CS = 1'b0;
		NEXTSTATE = CURRENTSTATE;

		unique case (CURRENTSTATE)

			WRITE_EN: begin
				unique case (count)
					5'd7,5'd6,5'd5,5'd4,5'd3,5'd2,5'd1,5'd0: begin
						CS = 1'b0;
						in_out[0] = instruction[count];
						NEXTSTATE = WRITE_EN;
					end
					5'h1F: begin
						CS = 1'b1;
						NEXTSTATE = WRITE_SR;
					end
				endcase
			end

			WRITE_SR: begin
				if(count==5'h1F && flag_instr_wsr==1) begin
					CS = 1'b1;
					NEXTSTATE = INSTRU_READ_SR;
				end else if(count <=5'd15) begin
					CS = 1'b0;
					in_out[0] = (flag_instr_wsr) ? status_reg1_2[count] : instruction[count];
					NEXTSTATE = WRITE_SR;
				end
			end

			INSTRU_READ_SR: begin
				unique case (count)
					5'd7,5'd6,5'd5,5'd4,5'd3,5'd2,5'd1: begin
						CS = 1'b0;
						in_out[0] = instruction[count];
						NEXTSTATE = INSTRU_READ_SR;
					end
					5'h00: begin
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
						if (CLOCK==1) begin
							NEXTSTATE = IDLE;
						end
					end else begin
						NEXTSTATE = READ_SR;
					end
				end		
			end

			IDLE: begin
				CS = 1'b1;
				if (flag_end_init) begin
					NEXTSTATE = IDLE;
				end else if(busmem.ARESETn) begin
					NEXTSTATE=WRITE_EN;
				end
			end
		endcase
	  end else begin
			CS = 'z;
			in_out = 'z;
			NEXTSTATE = IDLE;
	  end
	end
endmodule