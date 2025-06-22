module uart_rx(
    input wire clk,
    input wire rst_n,
    input wire baud_clk,
    input wire rx,
    output reg [7:0] rx_data,
    output reg rx_valid
);

    localparam IDLE = 3'd0,
               START_DET = 3'd1,
               DATA_RX = 3'd2,
               PARITY_CHK = 3'd3,
               STOP_CHK = 3'd4;

    reg [2:0] state, next_state;
    reg [3:0] bit_cnt;
    reg [3:0] sample_cnt;
    reg [7:0] rx_data_reg;
    reg rx_reg;
    reg parity_bit;
    reg stop_bit;
    reg rx_ready;

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            sample_cnt <= 4'd0;
            rx_reg <= 1'b1;
        end else begin
            rx_reg <= rx;
            if (state == START_DET || state == DATA_RX || state == PARITY_CHK || state == STOP_CHK) begin
                if (sample_cnt == 4'd15) begin
                    sample_cnt <= 4'd0;
                end else begin
                    sample_cnt <= sample_cnt + 1'b1;
                end
            end else begin
                sample_cnt <= 4'd0;
            end
        end
    end

    always @(posedge clk or negedge rst_n) begin
        if (!rst_n) begin
            state <= IDLE;
            bit_cnt <= 4'd0;
            rx_data <= 8'd0;
            rx_valid <= 1'b0;
            rx_data_reg <= 8'd0;
            parity_bit <= 1'b0;
            stop_bit <= 1'b0;
            rx_ready <= 1'b1;
        end else begin
            state <= next_state;
            case (state)
                IDLE: begin
                    rx_valid <= 1'b0;
                    if (!rx_reg && rx_ready) begin
                        rx_ready <= 1'b0;
                        bit_cnt <= 4'd0;
                        next_state <= START_DET;
                    end else begin
                        next_state <= IDLE;
                    end
                end
                START_DET: begin
                    if (sample_cnt == 4'd7) begin
                        if (!rx_reg) begin
                            next_state <= DATA_RX;
                        end else begin
                            rx_ready <= 1'b1;
                            next_state <= IDLE;
                        end
                    end else begin
                        next_state <= START_DET;
                    end
                end
                DATA_RX: begin
                    if (sample_cnt == 4'd7) begin
                        rx_data_reg[bit_cnt] <= rx_reg;
                        if (bit_cnt < 4'd7) begin
                            bit_cnt <= bit_cnt + 1'b1;
                            next_state <= DATA_RX;
                        end else begin
                            bit_cnt <= bit_cnt + 1'b1;
                            next_state <= PARITY_CHK;
                        end
                    end else begin
                        next_state <= DATA_RX;
                    end
                end
                PARITY_CHK: begin
                    if (sample_cnt == 4'd7) begin
                        parity_bit <= rx_reg;
                        bit_cnt <= bit_cnt + 1'b1;
                        next_state <= STOP_CHK;
                    end else begin
                        next_state <= PARITY_CHK;
                    end
                end
                STOP_CHK: begin
                    if (sample_cnt == 4'd7) begin
                        stop_bit <= rx_reg;
                        if (stop_bit && (parity_bit == ^rx_data_reg)) begin
                            rx_data <= rx_data_reg;
                            rx_valid <= 1'b1;
                        end
                        rx_ready <= 1'b1;
                        next_state <= IDLE;
                    end else begin
                        next_state <= STOP_CHK;
                    end
                end
                default: next_state <= IDLE;
            endcase
        end
    end

endmodule