module uart_tx(
    input wire clk,
    input wire rst_n,
    input wire baud_clk,
    input wire tx_en,
    input wire [7:0] tx_data,
    output reg tx,
    output reg tx_done
);

    localparam IDLE = 4'd0,
               START = 4'd1,
               DATA = 4'd2,
               PARITY = 4'd3,
               STOP = 4'd4;

    reg [3:0] state, next_state;
    reg [3:0] bit_cnt;
    reg [7:0] tx_data_reg;
    reg parity_bit;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            bit_cnt <= 4'd0;
            tx_data_reg <= 8'd0;
            tx <= 1'b1;
            tx_done <= 1'b0;
            parity_bit <= 1'b0;
				
        end else begin
            state <= next_state;
            case (state)
                IDLE: begin
                    tx_done <= 1'b0;
                    if (tx_en) begin
                        tx_data_reg <= tx_data;
                        bit_cnt <= 4'd0;
                        parity_bit <= ^tx_data;
                        next_state <= START;
                    end else begin
                        next_state <= IDLE;
                    end
                end
					 
                START: begin
                    tx <= 1'b0;
                    if (baud_clk) begin
                        bit_cnt <= bit_cnt + 1'b1;
                        next_state <= DATA;
                    end else begin
                        next_state <= START;
                    end
                end
					 
                DATA: begin
                    tx <= tx_data_reg[bit_cnt];
                    if (baud_clk) begin
                        if (bit_cnt < 4'd7) begin
                            bit_cnt <= bit_cnt + 1'b1;
                            next_state <= DATA;
                        end else begin
                            bit_cnt <= bit_cnt + 1'b1;
                            next_state <= PARITY;
                        end
                    end else begin
                        next_state <= DATA;
                    end
                end
					 
                PARITY: begin
                    tx <= parity_bit;
                    if (baud_clk) begin
                        bit_cnt <= bit_cnt + 1'b1;
                        next_state <= STOP;
                    end else begin
                        next_state <= PARITY;
                    end
                end
					 
                STOP: begin
                    tx <= 1'b1;
                    if (baud_clk) begin
                        tx_done <= 1'b1;
                        next_state <= IDLE;
                    end else begin
                        next_state <= STOP;
                    end
                end
                default: next_state <= IDLE;
            endcase
        end
    end

endmodule