module AXI4l_slavedecerr (
  axi4_lite_if slavedecerr);

  import axi4_types::*;

  typedef enum logic{
    WAIT_ADDR,
    WAIT_RESP
  } state;

  state state_read;
  state state_write;

  always_ff @(posedge slavedecerr.ACLK) begin
    if(!slavedecerr.ARESETn) begin

      slavedecerr.awready <= 0;

      slavedecerr.wready <=0;

      slavedecerr.bvalid <=0;
      slavedecerr.bresp <= AXI4_RESP_L_OKAY;

      slavedecerr.arready <= 0;

      slavedecerr.rvalid <= 0;
      slavedecerr.rdata <= 0;
      slavedecerr.rresp <= AXI4_RESP_L_OKAY;

      state_write <= WAIT_ADDR;
      state_read <= WAIT_ADDR;

    end else begin

      case (state_read)
        WAIT_ADDR: begin
          slavedecerr.arready <= 1;
          if(slavedecerr.arvalid) begin
            slavedecerr.arready <= 0;

            slavedecerr.rvalid <= 1;	
            slavedecerr.rdata <= 32'd0;
            slavedecerr.rresp <= AXI4_RESP_L_DECERR;
            state_read <= WAIT_RESP;
          end 
        end
        WAIT_RESP: begin
          if(slavedecerr.rvalid && slavedecerr.rready) begin
            slavedecerr.rvalid <= 0;
            state_read <= WAIT_ADDR;
          end
        end
      endcase

      case (state_write)
        WAIT_ADDR: begin
          slavedecerr.awready <= 1;
          if(slavedecerr.awvalid) begin
            slavedecerr.awready <= 1'b0;
            slavedecerr.wready <= 1'b1;
            slavedecerr.bvalid <= 1'b1;
            slavedecerr.bresp <= AXI4_RESP_L_DECERR;
            state_write <= WAIT_RESP;
          end
        end
        WAIT_RESP: begin
          slavedecerr.wready <= 1'b0;
          if(slavedecerr.bvalid && slavedecerr.bready) begin
            slavedecerr.bvalid <= 1'b0;
            state_write <= WAIT_ADDR;
          end
        end
      endcase
   end
 end
endmodule
