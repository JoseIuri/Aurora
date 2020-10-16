class agentDummy_sequence extends uvm_sequence #(agentDummy_transaction);
`uvm_object_utils(agentDummy_sequence)

function new(string name="agentDummy_sequence");
    super.new(name);
endfunction: new

task body;
    agentDummy_transaction tr;
    tr = agentDummy_transaction::type_id::create("tr");
    start_item(tr);
        assert(tr.randomize());
    finish_item(tr);
endtask: body
endclass
