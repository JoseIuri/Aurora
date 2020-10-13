module axibus2flat_bridge (AXI_BUS.Master pul, axi4_lite_if flat);

    always_comb begin

        pul.aw_valid  = flat.awvalid ;
        flat.awready  = pul.aw_ready ;
        pul.aw_addr   = flat.awaddr  ;
        pul.aw_prot   = flat.awprot  ;
	pul.aw_region = 3'b000       ;
	pul.aw_len    = 8'h00        ;
	pul.aw_size   = 3'b000       ;
	pul.aw_burst  = 2'b00        ;
	pul.aw_lock   = 1'b0         ;
	pul.aw_cache  = 4'b0000      ;
	pul.aw_qos    = 4'b0000      ;
	pul.aw_id     = '0           ;
	pul.aw_user   = '0           ;

        pul.w_valid  = flat.wvalid  ;
        flat.wready  = pul.w_ready  ;
        pul.w_data   = flat.wdata   ;
        pul.w_strb   = flat.wstrb   ;
        pul.w_user   = '0           ;
        pul.w_last   = 1'b0         ;
                                    
        flat.bvalid  = pul.b_valid  ;
        pul.b_ready  = flat.bready  ;
        flat.bresp   = pul.b_resp   ;
                                    
        pul.ar_valid = flat.arvalid ;
        flat.arready = pul.ar_ready ;
        pul.ar_addr  = flat.araddr  ;
        pul.ar_prot  = flat.arprot  ;
	pul.ar_region = 3'b000       ;
	pul.ar_len    = 8'h00        ;
	pul.ar_size   = 3'b000       ;
	pul.ar_burst  = 2'b00        ;
	pul.ar_lock   = 1'b0         ;
	pul.ar_cache  = 4'b0000      ;
	pul.ar_qos    = 4'b0000      ;
	pul.ar_id     = '0           ;
	pul.ar_user   = '0           ;
                                    
        flat.rvalid  = pul.r_valid  ;
        pul.r_ready  = flat.rready  ;
        flat.rdata   = pul.r_data   ;
        flat.rresp   = pul.r_resp   ;

//  logic                      r_last;
//  logic [AXI_ID_WIDTH-1:0]   r_id;
//  logic [AXI_USER_WIDTH-1:0] r_user;

//  logic [AXI_ID_WIDTH-1:0]   b_id;
//  logic [AXI_USER_WIDTH-1:0] b_user;

    end


endmodule
    
