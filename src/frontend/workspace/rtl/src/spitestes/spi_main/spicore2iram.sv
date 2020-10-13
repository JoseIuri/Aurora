module spicore2iram  #(DATA_SIZE = 32)(
	input logic CLK,
	input logic CS,
	input logic ARESETn, 
	input logic [23:0]address,
	inout wire IO0, IO1, IO2, IO3

);

logic [DATA_SIZE-1:0]data;
logic [4:0] count;
logic [7:0] instruction;
logic [2:0] count_data;
logic set;

typedef enum logic[1:0]{
		INSTRUC,
		ADDR,
		DUMMY,
		WAIT
} state;

state NEXTSTATE;
state CURRENTSTATE;

typedef enum logic{
		IDLE,
		DATA
} state_neg;

//Using the IC W25Q64CV
//with Quad SPI Instructions

// IO0 -> DI
// IO1 -> DO
// IO2 -> /WP
// IO3 -> /HOLD

//Fast Read Quad Output = Instruction 6Bh


always_ff @(posedge CLK) begin
	if(ARESETn) begin
		data <= 0;
		count <= 7; 
		count_data <= 7;
		instruction <= 8'h6B;
		set <=1;
		CURRENTSTATE <= INSTRUC;
	end else begin
		if (!CS) begin
			CURRENTSTATE <= NEXTSTATE;
			case (CURRENTSTATE)

				INSTRUC: begin
					//count <=7;
					if(count<=7) begin
						count <= count-1;
					end
					if(count==0) begin
						count <= 24;
					end	
				end

				ADDR: begin
					if(count<=24) begin
						count <= count-1;
					end
					if(count==0) begin
						count <= 7;
					end						
				end

				DUMMY: begin
					if(count<=7) begin
						count <= count-1;
					end
					if(count==0) begin
						count <= 7;
					end						
				end

				WAIT: begin
					count <=7;
					if(count<=7) begin
						count <= count-1;
					end
					if(count==0) begin
						count <= 23;
					end	
				end

			endcase
		end
	end
end


always_comb begin 

	case (CURRENTSTATE)
		INSTRUC: begin
			if(count <=7) begin
				IO0 = instruction[count];
				IO1 = 'z;
				IO2 = 'z;	
				IO3 = 'z;
				NEXTSTATE = INSTRUC;
			end
			if(count==0) begin
				IO0 = instruction[count];
				IO1 = 'z;
				IO2 = 'z;	
				IO3 = 'z;
				NEXTSTATE = ADDR;
			end
		end
		ADDR: begin
			if (count <= 24) begin
				IO0 = address[count-1];
				IO1 = 'z;
				IO2 = 'z;	
				IO3 = 'z;
				NEXTSTATE = ADDR;
			end
			if(count==0) begin
				IO0 = address[count];
				IO1 = 'z;
				IO2 = 'z;	
				IO3 = 'z;
				NEXTSTATE = DUMMY;
			end
		end


		DUMMY: begin
			if(count<=7) begin
				NEXTSTATE = DUMMY;
			end
			if(count==0) begin
				NEXTSTATE = WAIT;//
			end
		end


		WAIT: begin  //Esse estado deve esperar o estado data da outra FSM
			if(set) begin
				NEXTSTATE = INSTRUC;
			end else begin
				NEXTSTATE = WAIT;
			end
		end

		DATA: begin
			count_data <=7;
			if(count_data==7) begin
				data[DATA_SIZE-1:DATA_SIZE-4] <= {IO0,IO1,IO2,IO3};
			end
			if(count_data==6) begin
				data[DATA_SIZE-5:DATA_SIZE-8] <= {IO0,IO1,IO2,IO3};
			end
			if(count_data==5) begin
				data[DATA_SIZE-9:DATA_SIZE-12] <= {IO0,IO1,IO2,IO3};
			end
			if(count_data==4) begin
				data[DATA_SIZE-13:DATA_SIZE-16] <= {IO0,IO1,IO2,IO3};
			end
			if(count_data==3) begin
				data[DATA_SIZE-17:DATA_SIZE-20] <= {IO0,IO1,IO2,IO3};
			end
			if(count_data==2) begin
				data[DATA_SIZE-21:DATA_SIZE-24] <= {IO0,IO1,IO2,IO3};
			end
			if(count_data==1) begin
				data[DATA_SIZE-25:DATA_SIZE-28] <= {IO0,IO1,IO2,IO3};
			end
			if(count_data==0) begin
				data[DATA_SIZE-29:0] <= {IO0,IO1,IO2,IO3};
				NEXTSTATE <= IDLE;
			end
		end


		//default : /* default */;
	endcase
end

endmodule
