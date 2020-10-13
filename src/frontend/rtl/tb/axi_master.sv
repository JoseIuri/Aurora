module axi_master (
	axi4_lite_if axibus,
	input logic [1:0]delay);

logic [1:0]cont;

	always_ff @(posedge axibus.ACLK) begin
		if(!axibus.ARESETn) begin

			 axibus.rready <= 0;
			 
			 axibus.arvalid <= 0;
			 axibus.araddr <= 0;
			 cont <= 0;

			 axibus.awvalid <= 0;
			 axibus.awaddr	<= 0;
			 axibus.awprot	<= 0;

			 axibus.wvalid	<= 0;
			 axibus.wdata	<= 0;
			 axibus.wstrb	<= 0;

			 axibus.bready	<= 0;
		end else begin

			cont <= cont+1;
			if(cont==delay-1) begin
				if (!axibus.arvalid) begin 
					axibus.arvalid <= 1;
					axibus.arprot <= $urandom_range(3,0);//3'b011;//
					axibus.araddr[9:0] <= $urandom_range(1023,0);

					axibus.araddr[11:10] <= $urandom_range(3,0);//slave;
					/*axibus.awaddr[11:10] <= $urandom_range(3,0);//slave;

					axibus.awaddr[9:0]	<= $urandom_range(1023, 0);
					axibus.wdata	<= $urandom_range(32);
					axibus.awvalid	<= 1;
					axibus.wvalid	<= 1;
					axibus.bready	<= 1;*/
				end
				cont <= cont+1;
			end
			
			if (cont==delay)begin cont <=0; end
			
			if(axibus.arvalid&&axibus.arready) begin 
				axibus.rready <= 1;
				axibus.arvalid <= 0;
			end	

			if (axibus.rvalid&&axibus.rready) begin
				$display("%0d dado: %h,	slave: %b",axibus.araddr[9:0]+1'd1,axibus.rdata,axibus.araddr[11:10]);
				$display("arprot: %b, 		rresp: %s",axibus.arprot, axibus.rresp);
				axibus.rready <= 0;
			end 
		end
	end
endmodule