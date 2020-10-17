class agentDummy_monitor extends uvm_monitor;

    // Attributes
    virtual agentDummy_interface vif;
    uvm_analysis_port #(agentDummy_transaction) req;
    uvm_analysis_port #(agentDummy_transaction) resp;
    string                              tID;

    protected agentDummy_transaction transCollected;

    `uvm_component_utils_begin(agentDummy_monitor)
    `uvm_component_utils_end

    ////////////////////////////////////////////////////////////////////////////////
    // Implementation
    //------------------------------------------------------------------------------
    function new(string name="agentDummy_monitor", uvm_component parent=null);
        super.new(name, parent);
        this.transCollected = agentDummy_transaction::type_id::create("transCollected");

        this.tID = get_type_name().toupper();
        this.ap = new("ap", this);
    endfunction: new

    function build_phase(uvm_phase phase);
        super.build_phase(phase);
        `uvm_info(tID, $sformatf("build_phase begin ..."), UVM_HIGH)
        if (!(uvm_config_db#(virtual agentDummy_interface)::get(this, "", "agentDummy_vif", vif))) begin
            `uvm_fatal("NOVIF", {"virtual interface must be set for: ", get_full_name(), ".vif"})
        end

    endfunction : build_phase

    task run_phase(uvm_phase phase);
        this.CollectTransactions(phase); // collector task
    endtask: run_phase

    task CollectTransactions(uvm_phase phase);

        forever begin
            phase.raise_objection(this);

            this.BusToTransaction();

            this.req.write(transCollected);
            

            phase.drop_objection(this);
        end
    endtask : CollectTransactions

    function void BusToTransaction();
        
    endfunction : BusToTransaction

endclass: agentDummy_monitor
