package axi4_types;

  typedef enum logic [1:0] {
  	AXI4_RESP_L_OKAY,
  	AXI4_RESP_L_EXOKAY, // not supported on AXI4-Lite
  	AXI4_RESP_L_SLVERR,
  	AXI4_RESP_L_DECERR
  } axi4_resp_el;
  
  typedef enum bit [1:0] {
  	AXI4_RESP_B_OKAY,
  	AXI4_RESP_B_EXOKAY, // not supported on AXI4-Lite
  	AXI4_RESP_B_SLVERR,
  	AXI4_RESP_B_DECERR
  } axi4_resp_eb;
  
  typedef struct packed {
  	logic instruction;
  	logic non_secure;
  	logic privileged;
  } axi4_prot_typel;	
  
  typedef struct packed {
  	bit instruction;
  	bit non_secure;
  	bit privileged;
  } axi4_prot_typeb;

endpackage
