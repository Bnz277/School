module uart_top(
    input wire clk,
    input wire rst_n,
    input wire rx,
    output wire tx,
    input wire [7:0] tx_data,
    input wire tx_en,
    output wire tx_done,
    output wire [7:0] rx_data,
    output wire rx_valid
);

    wire baud_clk;

    baud_gen baud_gen_inst(
        .clk(clk),
        .rst_n(rst_n),
        .baud_clk(baud_clk)
    );

    uart_tx uart_tx_inst(
        .clk(clk),
        .rst_n(rst_n),
        .baud_clk(baud_clk),
        .tx_en(tx_en),
        .tx_data(tx_data),
        .tx(tx),
        .tx_done(tx_done)
    );

    uart_rx uart_rx_inst(
        .clk(clk),
        .rst_n(rst_n),
        .baud_clk(baud_clk),
        .rx(rx),
        .rx_data(rx_data),
        .rx_valid(rx_valid)
    );

endmodule