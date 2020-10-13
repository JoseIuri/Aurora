module axi_addrmap  #(ADDR_SIZE = 12, SELECT = 2) (
	input logic [ADDR_SIZE-1:0] address_in,
	output logic [ADDR_SIZE-1:0] address_out,
	output logic [SELECT-1:0] select);

        always_comb begin

          unique case (address_in) inside

            [32'h1A100000 : (32'h1A106000-1'b1)]: begin
              select = 4'h7;
              address_out = address_in;
            end
            [32'h1A107000 : (32'h1A108000-1'b1)]: begin
              select = 4'h7;
              address_out = address_in;
            end
            [32'h19100000 : (32'h19101000-1'b1)]: begin
              select = 4'h0;
              address_out = address_in[11:0];
            end
            [32'h19101000 : (32'h19102000-1'b1)]: begin
              select = 4'h1;
              address_out = address_in[11:0];
            end
            [32'h19102000 : (32'h19103000-1'b1)]: begin
              select = 4'h2;
              address_out = address_in[11:0];
            end
            [32'h19103000 : (32'h19104000-1'b1)]: begin
              select = 4'h3;
              address_out = address_in[11:0];
            end
            [32'h19104000 : (32'h19105000-1'b1)]: begin
              select = 4'h4;
              address_out = address_in[11:0];
            end
            [32'h00008000 : (32'h00010000-1'b1)]: begin
              select = 4'h5;
              address_out = address_in - 32'h8000;
            end
            [32'h00000000 : (32'h00008000-1'b1)]: begin
              select = 4'h6;
              address_out = address_in;
            end

            default : begin
              select = 4'h8;
              address_out = address_in;
            end
          endcase

        end
endmodule
