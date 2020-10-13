module AXI_BUS_to_flat (AXI_BUS.Slave pul, axi4_lite_if flat);

    always_comb begin

        flat.awvalid = pul.aw_valid;
        pul.aw_ready  = flat.awready;
        flat.awaddr  = pul.aw_addr;
        flat.awprot  = pul.aw_prot;

        flat.wvalid  = pul.w_valid;
        pul.w_ready   = flat.wready;
        flat.wdata   = pul.w_data;
        flat.wstrb   = pul.w_strb;

        pul.b_valid   = flat.bvalid;
        flat.bready  = pul.b_ready;
        pul.b_resp    = flat.bresp;

        flat.arvalid = pul.ar_valid;
        pul.ar_ready  = flat.arready;
        flat.araddr  = pul.ar_addr;
        flat.arprot  = pul.ar_prot;

        pul.r_valid   = flat.rvalid;
        flat.rready  = pul.r_ready;
        pul.r_data    = flat.rdata;
        pul.r_resp    = flat.rresp;

    end


endmodule
    
