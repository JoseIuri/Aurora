/////////////// LER README.txt PARA ENTENDER O FUNCIONAMENTO

module spi_test_le_sr1e2  #(DATA_SIZE = 32)(
	axi4_lite_if busmem,
	inout IO0, IO1, IO2, IO3,
	output logic CS, CLOCK, flag_end,
	output logic [2:0]estado,
	output logic [7:0] status_reg_lido1, status_reg_lido2 //adicionado essa saida para ler o reg_status modificado
);
	logic [3:0] in_out;
	
	assign IO0 = in_out[0];
	assign IO1 = in_out[1];
	assign IO2 = in_out[2];
	assign IO3 = in_out[3];

	logic [2:0] count; // Contador para enviar instruções e para escrever ou ler o registrador de status;	
	logic [7:0] instruction;
	logic flag_not_busy;
	logic [15:0] status_reg1_2;
	

	typedef enum logic[1:0]{
		INSTRU_READ_SR,
		READ_SR,
		IDLE
	} state;

	state NEXTSTATE;
	state CURRENTSTATE;
	assign estado = CURRENTSTATE;

	always_ff @(posedge busmem.ACLK) begin
		if(!busmem.ARESETn) begin
			count <= 3'd7;
			instruction <= 8'h00;
			status_reg1_2 <= 16'h0000;
			flag_not_busy <= 0;
			flag_end <= 0;
			status_reg_lido1 <= 8'h00;
			status_reg_lido2 <= 8'h00;
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

				INSTRU_READ_SR: begin
					if(CLOCK == 1 && count<=3'd7) begin
						count <= count-1'b1;
						if(count==3'd0) begin
							count <= 3'd7;
						end
					end
				end

				READ_SR: begin
					if(count==0 && CLOCK ==1) begin
						if(IO1==0 && flag_not_busy ==0) begin
							flag_not_busy <= 1'b1;
						end else if (flag_not_busy) begin
							flag_end <= 1'b1;
						end
						if (flag_not_busy==0) begin
							status_reg_lido1[count] <= IO1;
						end else if (flag_not_busy) begin
							status_reg_lido2[count] <= IO1;
						end
						count <= 3'd7;
					end else if(count<=3'd7 && CLOCK ==1) begin
						if (flag_not_busy==0) begin
							status_reg_lido1[count] <= IO1;
						end else if (flag_not_busy) begin
							status_reg_lido2[count] <= IO1;
						end
						count <= count-1'b1;
					end
				end

				IDLE: begin
					if(flag_not_busy) begin
						instruction <= 8'h35;
					end else begin
						instruction <= 8'h05;
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

			INSTRU_READ_SR: begin
				unique case (count)
					3'd7,3'd6,3'd5,3'd4,3'd3,3'd2,3'd1: begin
						CS = 1'b0;
						in_out[0] = instruction[count];
						NEXTSTATE = INSTRU_READ_SR;
					end
					3'd0: begin
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
					if(IO1==0 || flag_not_busy) begin
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
				if (flag_end) begin
					NEXTSTATE = IDLE;
				end else if(busmem.ARESETn) begin
						NEXTSTATE=INSTRU_READ_SR;
				end
			end
		endcase
	end
endmodule