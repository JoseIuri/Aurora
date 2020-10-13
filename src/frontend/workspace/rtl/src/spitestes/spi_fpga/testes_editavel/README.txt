#################### spi_resetcs.sv #####################

Esse módulo realiza o Chip Erase (coloca toda a memória para 1s (FFh))
Esse módulo precisa dos seguintes arquivos: axi4_lite_if.sv, axi4_types.sv,
mem_reset.sv e topteste.sv.

Segue a máquina de estados:
=> IDLE: se está no reset, continua no estado IDLE;
	 se não está no reset, vai para o estado WRITE_EN;
	 se terminou (flag_end==1), permanece no estado IDLE.
=> WRITE_EN: manda a instrução 06h em IO0 para setar o bit WEL do registrador
de estados (condição necessária para o dispositivo aceitar a próxima instrução),
em seguida vai para o estado RESET_C.
=> RESET_C: manda a instrução C7h em IO0, aqui a memória é setada em 1s, em
seguida, vai para o estado INSTRU_READ_SR.
=> INSTRU_READ_SR: manda a instrução 05h em IO0 para habilitar a leitura no 
registrador de status 1 (que contêm os bits WEL e BUSY), em seguida, vai para
o estado READ_SR.
=> READ_SR: fica lendo em IO1 o registrador de status 1 até que o bit BUSY
seja zero, quando isso acontecer, a flag_end é setada para 1 e o estado volta
para IDLE.


#################### spi_test_we.sv #####################

Esse módulo lê o SR1 (Status Register 1) antes e depois da instrução
WE (Write Enable), a qual modifica o bit S1 (WEL).
Esse módulo precisa dos seguintes arquivos: axi4_lite_if.sv, axi4_types.sv,
mem_test_we.sv e topteste.sv.

Segue a máquina de estados:
=> IDLE: se está no reset, continua no IDLE;
	 se não está no reset, vai para WRITE_EN;
	 se terminou (flag_end==1), permanece no IDLE.
=> INS_READ_SR: manda a instrução 05h em IO0 para habilitar a leitura no 
registrador de status 1 (que contêm os bits WEL e BUSY), em seguida, vai para
READSR.
=> READSR: lê em IO1 o registrador de status 1 e armazena em status_reg_lido1,
em seguida, vai para WRITE_EN.
=> WRITE_EN: manda a instrução 06h em IO0 para setar o bit WEL do registrador
de estados em seguida vai para o estado INSTRU_READ_SR.
=> INSTRU_READ_SR: manda a instrução 05h em IO0 para habilitar a leitura no
registrador de status 1 (que contêm os bits WEL e BUSY), em seguida, vai para
o estado READ_SR.
=> READ_SR: fica lendo em IO1 o registrador de status 1 (e armazenando em 
status_reg_lido1) até que o bit BUSY seja zero, quando isso acontecer, a flag_end
é setada para 1 e o estado volta para IDLE.


#################### spi_test_init.sv #####################

Esse módulo faz o quad enable no chip e lê SR1 e SR2 em seguida.
Esse módulo precisa dos seguintes arquivos: axi4_lite_if.sv, axi4_types.sv,
mem_test_init.sv e topteste.sv.

Segue a máquina de estados:
=> IDLE: se está no reset, continua no IDLE;
	 se não está no reset e a flag_not_busy==0 (default), vai para WRITE_EN;
	 se não está no reset e a flag_not_busy==1, vai para INSTRU_READ;
	 se terminou (flag_end==1), permanece no IDLE.
=> WRITE_EN: manda a instrução 06h em IO0 para setar o bit WEL do registrador
de estados em seguida vai para o estado WRITE_SR.
=> WRITE_SR: manda a instrução 01h em IO0 para permitir que os Status Register
sejam escritos, em seguida, também em IO0 é enviado 0202h para escrever no status
register 1 e 2, respectivamente - 02h em SR2 habilita o QE, depois vai para
INSTRU_READ_SR.
=> INSTRU_READ_SR: manda a instrução 05h em IO0 para habilitar a leitura no
registrador de status 1 (que contêm os bits WEL e BUSY), em seguida, vai para
o estado READ_SR.
=> READ_SR: fica lendo em IO1 o registrador de status 1 (e armazenando em 
status_reg_lido1) até que o bit BUSY seja zero, quando isso acontecer, a flag_not_busy
é setada para 1 e o estado volta para IDLE.
=> IDLE: Depois de voltar para IDLE com flag_not_busy=1, vai para INSTRU_READ com 
instruction = 8'h35, pois já realizou os passos de quad enable, agora queremos
ler o status register 2 para ter certeza que o bit QE = 1;
=> INSTRU_READ_SR e READ_SR: Repete essas instruções, para ler o status register 2,
(e armazenando em status_reg_lido2), quando terminar a leitura, a flag_end é
setada para 1 e o estado volta para IDLE.
