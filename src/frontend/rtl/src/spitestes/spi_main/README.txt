README


O módulo spi.sv é o módulo que se conecta diretamente com a memória que temos (winbond 25Q32BVA1G) e possui uma interface AMBA AXI4-Lite.

A interface AMBA foi feita para se comunicar com o mestre (módulo master_spi.sv).

Para se comunicar com o chip da memória temos os quatro bits (pinos) de entrada e saída de dados (IO0, IO1, IO2 e IO3) e um bit (pino) de CS (chip select).
Além disso, precisaremos de um bit para se conectar ao pino de CLOCK




vcs -sverilog -debug_pp +vcs+vcdpluson spicore2iram.sv topteste.sv -R