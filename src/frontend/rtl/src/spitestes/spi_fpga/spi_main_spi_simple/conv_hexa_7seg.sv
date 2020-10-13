module Conv_Hexa_7seg (Entrada, Saida);

input [3:0] Entrada;
output reg [6:0] Saida;

always @ (*)
	case (Entrada)
		4'd0: Saida = 7'b1_000_000; 
		4'd1: Saida = 7'b1_111_001; 
		4'd2: Saida = 7'b0_100_100; 
		4'd3: Saida = 7'b0_110_000; 
		4'd4: Saida = 7'b0_011_001; 
		4'd5: Saida = 7'b0_010_010; 
		4'd6: Saida = 7'b0_000_010;
		4'd7: Saida = 7'b1_111_000;
		4'd8: Saida = 7'b0_000_000;
		4'd9: Saida = 7'b0_010_000;
		4'd10: Saida = 7'b0_001_000;
		4'd11: Saida = 7'b0_000_011;
		4'd12: Saida = 7'b1_000_110;
		4'd13: Saida = 7'b0_100_001;
		4'd14: Saida = 7'b0_000_110;
		4'd15: Saida = 7'b0_001_110;
	endcase
	
endmodule