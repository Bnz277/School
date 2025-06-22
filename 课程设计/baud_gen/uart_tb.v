module uart_tb;

    reg clk;
    reg rst_n;
    reg rx;
    reg [7:0] tx_data;
    reg tx_en;
    wire tx;
    wire tx_done;
    wire [7:0] rx_data;
    wire rx_valid;

    initial begin
        clk = 1'b0;
        forever #10 clk = ~clk;
    end

    initial begin
        rst_n = 1'b0;
        #100 rst_n = 1'b1;
    end

    uart_top uut(
        .clk(clk),
        .rst_n(rst_n),
        .rx(rx),
        .tx(tx),
        .tx_data(tx_data),
        .tx_en(tx_en),
        .tx_done(tx_done),
        .rx_data(rx_data),
        .rx_valid(rx_valid)
    );

    initial begin
        #200;
        tx_data = 8'h55;
        tx_en = 1'b1;
        #20;
        tx_en = 1'b0;
		  
        wait(tx_done);
        #100;

        rx = 1'b1;
        #1000;
        
        rx = 1'b0;
        #1300;
		  
        rx = 1'b0; #1300;
        rx = 1'b1; #1300;
        rx = 1'b0; #1300;
        rx = 1'b1; #1300;
        rx = 1'b0; #1300;
        rx = 1'b1; #1300;
        rx = 1'b0; #1300;
        rx = 1'b1; #1300;
        
        rx = 1'b0; #1300;
        
        rx = 1'b1; #1300;
        
        wait(rx_valid);
        $display("接收数据: 0x%h", rx_data);
        
        #100;
        $finish;
    end

endmodule