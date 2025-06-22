module baud_gen(
    input wire clk,
    input wire rst_n,
    output reg baud_clk
);

    parameter BAUD_RATE = 115200;
    parameter SYS_CLK = 50_000_000;
    parameter DIVIDER = SYS_CLK / (BAUD_RATE * 16) - 1;

    reg [15:0] cnt;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            cnt <= 16'd0;
            baud_clk <= 1'b0;
				
        end else if (cnt == DIVIDER) begin
            cnt <= 16'd0;
            baud_clk <= ~baud_clk;
				
        end else begin
            cnt <= cnt + 1'b1;
            baud_clk <= baud_clk;
				
        end
    end

endmodule


