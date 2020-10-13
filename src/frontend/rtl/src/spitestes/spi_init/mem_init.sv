module mem_init  #(DATA_SIZE = 32)(
	axi4_lite_if busmem,
	inout IO0, IO1, IO2, IO3,
	input logic CS, CLOCK, VCC, GND, flag_end_init
);
	logic [3:0] in_out;
	
	assign IO0 = in_out[0];
	assign IO1 = in_out[1];
	assign IO2 = in_out[2];
	assign IO3 = in_out[3];

	logic flag;
	logic [4:0] count;	
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

	//Using the IC W25Q64CV
	//with Quad SPI Instructions

	// IO0 -> DI
	// IO1 -> DO
	// IO2 -> /WP
	// IO3 -> /HOLD

	always_ff @(posedge busmem.ACLK) begin
		if(!busmem.ARESETn) begin
			count <= 5'd7; 
			flag_instr_wsr <= 0;
			//CLOCK<=0;
			flag <=0;
			
			CURRENTSTATE <= IDLE;

		end else begin
			CURRENTSTATE <= NEXTSTATE;

			case (CURRENTSTATE)
				WRITE_EN: begin
					if(count == 5'h1F) begin
						count <= 5'd7; 
					end else if(CLOCK == 1) begin
						count <= count-1;
					end
				end

				WRITE_SR: begin
					if(flag_instr_wsr && count==5'h1F) begin
						count <= 5'd7;
					end
					if(CLOCK == 1) begin
						count <= count-1;
						if(flag_instr_wsr==0 && count==0) begin
							count <= 5'd15;
							flag_instr_wsr <=1;
						end
					end
				end


				INSTRU_READ_SR: begin
					if(CLOCK == 1) begin
						if(count<=5'd8) begin
							count <= count-1;
						end
						if(count==5'h00) begin
							count <= 5'd7;
						end
					end
				end

				READ_SR: begin
					if(count==5'd8) begin
						count<=count-1;
					end
					if(CLOCK ==1) begin
						if(count<=5'd7) begin
							count <= count-1;
						end
						if(count==0) begin
							flag <=1; //Flag criada para demorar mais para mem.sv simular a subida o bit de BUSY
							count <= 5'd7;
						end	
					end					
				end
			endcase
		end
	end



	always_comb begin 
		in_out = 4'hz;
		NEXTSTATE = CURRENTSTATE;

		unique case (CURRENTSTATE)

			WRITE_EN: begin
				if(count==5'h1F) begin
					NEXTSTATE = WRITE_SR;
				end else if(count <=5'd7) begin
					instruction[count] = IO0;
					NEXTSTATE = WRITE_EN;
				end
			end

			WRITE_SR: begin
				if(count==5'h1F && flag_instr_wsr==1) begin
					NEXTSTATE = INSTRU_READ_SR;
				end else if(count <=5'd15) begin
					if(flag_instr_wsr==0) begin
						instruction[count] = IO0;
					end else if(flag_instr_wsr ==1) begin
						status_reg1_2[count] = IO0;
					end
					NEXTSTATE = WRITE_SR;
				end
			end


			INSTRU_READ_SR: begin
				if(count <=5'd7) begin
					instruction[count] = IO0;
					NEXTSTATE = INSTRU_READ_SR;
				end
				if(count==5'h00) begin
					instruction[count] = IO0;
					if(CLOCK==1) begin
						NEXTSTATE = READ_SR;
					end
				end
			end

			READ_SR: begin
				NEXTSTATE = READ_SR;
				if(count==0) begin
					if(flag==0) begin
						in_out[1]=1;
						NEXTSTATE = READ_SR; 
					end else if(flag==1) begin
						in_out[1]=0;
						//NEXTSTATE = READ_SR; 
					
						if(CLOCK==1) begin 
							NEXTSTATE = IDLE; 
						end 
					end
				end	 else if(count <=5'd7) begin
					in_out[1]=1;
					NEXTSTATE = READ_SR;
				end			
			end

			IDLE: begin
				NEXTSTATE = IDLE;


				if (flag_end_init) begin
					NEXTSTATE = IDLE;
				end else if(busmem.ARESETn) begin
					NEXTSTATE=WRITE_EN;
				end 

			end
		endcase
	end
endmodule