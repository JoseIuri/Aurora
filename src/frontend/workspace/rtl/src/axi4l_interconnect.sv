module axi4l_interconnect #(DATA_SIZE = 32, ADDR_SIZE = 10, int SLAVES = 4, SELECT = $clog2(SLAVES)) (
	axi4_lite_if master,
	axi4_lite_if slave[SLAVES-1:0],
	input logic [SELECT-1:0]selectread, selectwrite,
	input logic [ADDR_SIZE-1:0]addrread, addrwrite);

	import axi4_types::*;

	typedef enum logic{
		WAIT_ADDR,
		WAIT_RESP
	} state;

	state state_write;
	state state_read;

	logic [SELECT-1:0]auxread, auxwrite;
	logic [SELECT-1:0]writechannels, readchannels;

	//Sinais para "gambiarra"
	logic awready[SLAVES-1:0];
	logic wready[SLAVES-1:0];
	logic bvalid[SLAVES-1:0];
	logic[1:0] bresp[SLAVES-1:0];
	logic arready[SLAVES-1:0];
	logic rvalid[SLAVES-1:0];
	logic [DATA_SIZE-1:0]rdata[SLAVES-1:0];
	logic[1:0] rresp[SLAVES-1:0];


	generate for (genvar i = 0; i < SLAVES; ++i) always_comb begin
			//Write Address Channel
			slave[i].awvalid = (writechannels == i) ? master.awvalid : 0;
			slave[i].awaddr = (writechannels == i)? addrwrite : 0;
			slave[i].awprot = (writechannels == i)? master.awprot : 0;

			//Write Data Channel
			slave[i].wvalid = (writechannels == i)? master.wvalid : 0;
			slave[i].wdata = (writechannels == i)? master.wdata : 0;
			slave[i].wstrb = (writechannels == i)? master.wstrb : 0;

			//Write Response Channel
			slave[i].bready = (writechannels == i)? master.bready : 0;

			//Read Address Channel
			slave[i].arvalid = (readchannels == i)? master.arvalid : 0;
			slave[i].araddr = (readchannels == i)? addrread : 0;
			slave[i].arprot = (readchannels == i)? master.arprot : 0;

			//Read Data Channel
			slave[i].rready = (readchannels == i)? master.rready : 0;

			//Gambiarra para transformar um array de interfaces em um "array simples"
			awready[i] = slave[i].awready;
			wready[i] = slave[i].wready;
			bvalid[i] = slave[i].bvalid;
			bresp[i] = slave[i].bresp;
			arready[i] = slave[i].arready;
			rvalid[i] = slave[i].rvalid;
			rdata[i] = slave[i].rdata;
			rresp[i] = slave[i].rresp;
			
	end endgenerate

	always_comb begin

		readchannels = (state_read == WAIT_ADDR) ? selectread : auxread;
		writechannels = (state_write == WAIT_ADDR) ? selectwrite : auxwrite;
		//readchannels = (state_read == WAIT_ADDR) ? selectread:auxread;		
		//writechannels = (state_write == WAIT_ADDR) ? selectwrite:auxwrite;

		//Write Address Channel
		//master.awready = slave[selectwrite].awready;
		master.awready = awready[writechannels];

		//Write Data Channel
		master.wready = wready[writechannels];

		//Write Response Channel
		master.bvalid = bvalid[writechannels];
		master.bresp = bresp[writechannels];

		//Read Address Channel
		master.arready = arready[readchannels];

		//Read Data Channel
		master.rvalid = rvalid[readchannels];
		master.rdata = rdata[readchannels];
		master.rresp = rresp[readchannels];

	end

	always_ff @(posedge master.ACLK) begin
		if(!master.ARESETn) begin
			state_write <= WAIT_ADDR;
			state_read <= WAIT_ADDR;
			auxread <= 0;
			auxwrite <= 0;
		end else begin

			case (state_read)
				WAIT_ADDR: begin
							if(master.arvalid) begin
								auxread <= selectread;//escolhe slave[i]
								state_read <= WAIT_RESP; end 
							end
				WAIT_RESP: begin
							if(master.rvalid && master.rready) begin
								state_read <= WAIT_ADDR;
							end
						   end
			endcase


			case (state_write)
				WAIT_ADDR: begin
							if(master.awvalid) begin
								auxwrite <= selectwrite;
								state_write <= WAIT_RESP; end
							end
				WAIT_RESP: begin
							if(master.bvalid && master.bready) begin
								state_write <= WAIT_ADDR;
							end
						   end
			endcase

		end
	end
endmodule
