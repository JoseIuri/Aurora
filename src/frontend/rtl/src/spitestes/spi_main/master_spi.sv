module master_spi (
	axi4_lite_if master//,
	//input flag_end_data
);

	logic [31:0]mem[0:1023];
	logic [31:0]matchcount;
	logic [31:0]mismatchcount;
	initial begin
		$readmemh("dataMemo.txt", mem);
	end

	logic [master.ADDR_SIZE-1:0]address;
	typedef enum logic{
		WAIT_ADDR,
		WAIT_RESP
	} state;

	state STATE;

	//logic []
	always_ff @(posedge master.ACLK) begin
		if(!master.ARESETn) begin			 

			 //Read Address Channel
			 //recebe .arready
			 //estamos ignorando .arprot
			 master.arvalid <= 0;
			 master.araddr <= 0;

			 //Read Data Channel
			 //Vamos receber .rvalid, .rdata e .rresp
 			 master.rready <= 0;
 			 //address <= 16'h0F0F;

			matchcount <= 0;
			mismatchcount <= 0;

 			 STATE <= WAIT_ADDR;
		end else begin
			case (STATE)
				WAIT_ADDR: begin
					if(!master.arvalid) begin
						master.arvalid <= 1;
						master.araddr <= $urandom_range(1023,0);//address;
						STATE <= WAIT_ADDR;
					end
					if (master.arready && master.arvalid) begin
						master.rready <= 1;
						master.arvalid <= 0;
						STATE <= WAIT_RESP;
					end 
				end
				WAIT_RESP: begin
					//master.arvalid <=0;
					if(master.rvalid && master.rready /*&& flag_end_data*/) begin
						master.rready <= 0;
						STATE <= WAIT_ADDR;
						if(master.rdata==mem[master.araddr]) begin
							matchcount = matchcount+1'b1;
						end else begin
							mismatchcount = mismatchcount+1'b1;
						end
						$display("MASTER %0d dado: %h, memoriatxt: %h",master.araddr+1'd1,master.rdata, mem[master.araddr]);
						$display("MASTER rresp: %s", master.rresp);
						$display("match: %0d e mismatch: %0d", matchcount, mismatchcount);
					end else if (!master.rvalid) begin
						master.rready <= 1;
						STATE <= WAIT_RESP;
					end
				end
			endcase 
		end
	end

endmodule