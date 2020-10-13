module div_freq (
	input logic ARESETn, ACLK,
	output logic clk_1
);

	logic [24:0] Clock_1;

	always_ff @(posedge ACLK) begin
			if (Clock_1 <= 6250000) begin
				Clock_1 <= Clock_1 + 1'b1;
			end else begin
				Clock_1 <= '0;
				clk_1 <= ~clk_1;
		end
	end
endmodule