/**
  ******************************************************************************
  *
  * @university UFCG (Universidade Federal de Campina Grande)
  * @lab        embedded
  * @project    RISC-V.br
  * @ip         AES (Advanced Encryption Standard)
  *
  * @file       hierarchical2flat.sv
  *
  * @authors    Lucas Eliseu
  *
  ******************************************************************************
**/

module flat2hierarchical (axi4_lite_hierarchical hier, axi4_lite_if flat);

    always_comb begin

  	hier.AW.VALID = flat.awvalid;
        flat.awready  = hier.AW.READY;
        hier.AW.ADDR  = flat.awaddr;
        hier.AW.PROT  = flat.awprot;

        hier.W.VALID  = flat.wvalid;
        flat.wready   = hier.W.READY;
        hier.W.DATA   = flat.wdata;
        hier.W.STRB   = flat.wstrb;

        flat.bvalid   = hier.B.VALID;
        hier.B.READY  = flat.bready;
        flat.bresp    = hier.B.RESP;

        hier.AR.VALID = flat.arvalid;
        flat.arready  = hier.AR.READY;
        hier.AR.ADDR  = flat.araddr;
        hier.AR.PROT  = flat.arprot;

        flat.rvalid   = hier.R.VALID;
        hier.R.READY  = flat.rready;
        flat.rdata    = hier.R.DATA;
        flat.rresp    = hier.R.RESP;
    end

endmodule
