interface aw#(
    int unsigned SIZE_WORD = 32
    )();
        import axi4_types::*;
	logic VALID;
	logic READY;
	logic [SIZE_WORD-1:0]ADDR;      
	logic [2:0]PROT;
endinterface

interface w#(
    int unsigned SIZE_WORD = 32,
    int unsigned SIZE_STRB = 4
    )();
        import axi4_types::*;
	logic VALID;
	logic READY;
	logic [SIZE_WORD-1:0]DATA;
	logic [SIZE_STRB-1:0]STRB; 		
endinterface

interface b#(
    int unsigned SIZE_WORD = 32
    )();
        import axi4_types::*;
	logic VALID;
	logic READY;
	logic[1:0] RESP;
endinterface

interface ar#(
    int unsigned SIZE_WORD = 32
    )();
        import axi4_types::*;
	logic VALID;
	logic READY;
	logic [SIZE_WORD-1:0]ADDR;
	logic [2:0]PROT;
endinterface

interface r#(
    int unsigned SIZE_WORD = 32
    )();
        import axi4_types::*;
	logic VALID;
	logic READY;
	logic [SIZE_WORD-1:0]DATA;
	logic[1:0] RESP;
endinterface

interface axi4_lite_hierarchical# (
	// Constantes default: 
	// 		Palavras de 32 bits
	// 		4 bytes
	int SIZE_WORD=32
	) (
	input logic ACLK,
	input logic ARSTn);

	localparam SIZE_STRB = (SIZE_WORD/8); 

        import axi4_types::*;
	// WRITE CHANNEL
	aw#(.SIZE_WORD(SIZE_WORD)) AW();
	w#(.SIZE_WORD(SIZE_WORD), .SIZE_STRB(SIZE_STRB))   W();
	b#(.SIZE_WORD(SIZE_WORD))   B();
	// END

	// READ CHANNEL
	ar#(.SIZE_WORD(SIZE_WORD)) AR();
	r#(.SIZE_WORD(SIZE_WORD))   R();
	// END
endinterface
