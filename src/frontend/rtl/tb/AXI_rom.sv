module AXI_rom (
	axi4_lite_if rif
);

	import axi4_types::*;

	logic [31:0]mem[0:1023];

	initial begin
		$readmemh("dataMemo.txt", mem);
	end



//								 ROM
//   		    Seguro  		  |			 Não Seguro
//	 _____________  _____________  _____________  _____________
//	|_____________||_____________||_____________||_____________|
//  0      	  	 255    	    511     		767       	1023
//   
//	 Não Privilegiado | 	  Privilegiado	   | Não Privilegiado

/*
APROT [abc]
a - Dados ou instrução (0 ou 1)
b - Seguro ou não seguro (0 ou 1)
c - Não privilegiado ou Privilegiado (0 ou 1)

000 0-255 (Seguro e não privilegiado)
001 0-511 (Seguro e privilegiado)
010 768-1023 e 0-255 (Não seguro e não privilegiado)
011 0-1023 (Não seguro e privilegiado)

100
101
110
111
*/

	always_ff @(posedge rif.ACLK) begin
		if(!rif.ARESETn) begin
			 rif.arready <= 0;
			 rif.rvalid <= 0;
			 rif.rdata <= 0;
			 //rif.rresp <= AXI4_RESP_L_OKAY;
			 rif.awready <= 0;
			 rif.wready <=0;
			 rif.bvalid <=0;
			//rif.bresp <= AXI4_RESP_L_OKAY;
		end else begin
			if (!rif.arready) begin
				rif.arready <= 1;
			end
			if(rif.arvalid&&rif.arready) begin 
				rif.rvalid <= 1;
				//rif.rdata <= mem[rif.araddr];		
				rif.arready <= 0;
			end	
			if (rif.rvalid&&rif.rready) begin
				rif.arready <= 1;
				rif.rvalid <= 0;
			end 
		end


		if(rif.awvalid || rif.wvalid) begin
			rif.bresp	<= AXI4_RESP_L_SLVERR;
			rif.bvalid	<= 1;
		end

		casez (rif.arprot)
			3'b?00: begin
						if(rif.araddr/*[9:0]*/<= 255) begin
							rif.rresp <= AXI4_RESP_L_OKAY;
							if(rif.arvalid&&rif.arready) begin
								rif.rdata <= mem[rif.araddr/*[9:0]*/];end 
						end else begin
							rif.rresp <= AXI4_RESP_L_SLVERR;
						end
					end
			3'b?01: begin
						if(rif.araddr/*[9:0]*/ <= 511) begin
							rif.rresp <= AXI4_RESP_L_OKAY;
							if(rif.arvalid&&rif.arready)
								rif.rdata <= mem[rif.araddr/*[9:0]*/];
						end else begin
							rif.rresp <= AXI4_RESP_L_SLVERR;
						end
					end
			3'b?10: begin
						if(rif.araddr/*[9:0]*/ >= 768 || rif.araddr/*[9:0]*/ <= 255) begin
							rif.rresp <= AXI4_RESP_L_OKAY;
							if(rif.arvalid&&rif.arready)
								rif.rdata <= mem[rif.araddr/*[9:0]*/];
						end else begin
							rif.rresp <= AXI4_RESP_L_SLVERR;
						end
					end
			3'b?11: begin
						rif.rresp <= AXI4_RESP_L_OKAY;
						if(rif.arvalid&&rif.arready)begin
							rif.rdata <= mem[rif.araddr/*[9:0]*/];
						end 
					end
		endcase


	end
endmodule
