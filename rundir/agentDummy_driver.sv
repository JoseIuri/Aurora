class agentDummy_driver extends uvm_driver #(agentDummy_transaction);

    agentDummy_transaction req;
    string                tID;

    `uvm_component_utils_begin(agentDummy_driver)
    `uvm_component_utils_end

    // Attributes
    virtual agentDummy_interface vif;

    // Methods
    extern function new (string name="agentDummy_driver", uvm_component parent=null);
    extern function void build_phase(uvm_phase phase);
    extern task run_phase (uvm_phase phase);
    extern task DriveItem(agentDummy_transaction item);

endclass : agentDummy_driver


function agentDummy_driver::new(string name="agentDummy_driver", uvm_component parent=null);
    super.new(name, parent);
    this.tID = get_type_name().toupper();
endfunction : new

//------------------------------------------------------------------------------
// Build
//
function void agentDummy_driver::build_phase(uvm_phase phase);
    super.build_phase(phase);
    `uvm_info(tID, $sformatf("build_phase begin ..."), UVM_HIGH)

    // Get virtual interface from uvm_config_db
    if (!uvm_config_db#(virtual agentDummy_interface)::get(this, "", "agentDummy_vif", this.vif)) begin
        `uvm_fatal("NOVIF", {"virtual interface must be set for: ", get_full_name(), ".vif"})
    end
endfunction : build_phase

//------------------------------------------------------------------------------
// Get and process items
//
task agentDummy_driver::run_phase(uvm_phase phase);
    // INIT BLOCK
    forever begin
        // Get the next data item from sequencer
        seq_item_port.get_next_item(req);
        phase.raise_objection(this);
        // Execute the item
        this.DriveItem(req);
        seq_item_port.item_done();
        phase.drop_objection(this);
    end
endtask : run_phase

//------------------------------------------------------------------------------
// Drive sequence item
//
task agentDummy_driver::DriveItem(agentDummy_transaction item);
    // Add your logic here

    

endtask : DriveItem
