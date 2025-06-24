`timescale 1ns/1ps

module half_clk_tb;

    // 定义测试平台信号
    reg clk_in;
    reg reset;
    wire clk_out;

    // 实例化被测模块
    half_clk uut (
        .reset(reset),
        .clk_in(clk_in),
        .clk_out(clk_out)
    );

    // 生成时钟信号：周期为10ns（频率100MHz）
    initial begin
        clk_in = 0;
        forever #5 clk_in = ~clk_in;  // 每5ns翻转一次，得到10ns周期
    end

    // 测试过程
    initial begin
        $monitor("At time %t: reset=%b, clk_in=%b, clk_out=%b", $time, reset, clk_in, clk_out);

        // 初始化
        reset = 0;
        #20;  // 保持复位一段时间

        // 释放复位，开始正常工作
        reset = 1;
        #80;  // 观察几个周期的输出

        // 再次施加复位
        reset = 0;
        #20;

        // 结束仿真
        $finish;
    end

endmodule