module master_spi (
	axi4_lite_if master
);

	localparam int BUSMEM_ADDR_SIZE = $bits(master.araddr);
	localparam int BUSMEM_DATA_SIZE = $bits(master.rdata);

	typedef enum logic{
		WAIT_ADDR,
		WAIT_RESP
	} state;

	state STATE;
	

	always_ff @(posedge master.ACLK) begin
		if(!master.ARESETn) begin			 

			 //Read Address Channel
			 //recebe .arready
			 //estamos ignorando .arprot
			 master.arvalid <= 0;
			 master.araddr <=  24'h000000;

			 //Read Data Channel
			 //Vamos receber .rvalid, .rdata e .rresp
 			 master.rready <= 0;

 			 STATE <= WAIT_ADDR;
		end else begin
			case (STATE)
				WAIT_ADDR: begin
					if(!master.arvalid) begin
						master.arvalid <= 1;
						//master.araddr <= $urandom_range(1023,0)
						if(master.araddr<= 24'h0004FF) begin
							master.araddr <= master.araddr + 4'hA;
						end else begin
							master.araddr <= 24'h000000;
						end
						STATE <= WAIT_ADDR;
					end
					if (master.arready && master.arvalid) begin
						master.rready <= 1;
						//master.arvalid <= 0;
						STATE <= WAIT_RESP;
					end 
				end
				WAIT_RESP: begin
					master.arvalid <=0;
					if(master.rvalid && master.rready) begin
						master.rready <= 0;
						STATE <= WAIT_ADDR;
					end else if (!master.rvalid) begin
						master.rready <= 1;
						STATE <= WAIT_RESP;
					end
				end
			endcase 
		end
	end

endmodule