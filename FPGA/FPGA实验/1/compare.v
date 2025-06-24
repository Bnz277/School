//(方法一)：
//---------------文件名 compare.v -----------------
module compare(equal,a,b);
input a,b;
output equal;
   assign  equal = (a==b)? 1 : 0;  
   //a等于b时，equal输出为1；a不等于b时，equal输出为0。
endmodule


/*
//(方法二)：
module compare(equal,a,b);
input a,b;
output equal;
reg equal;
   always @(a or b)
     if(a==b)   //a等于b时，equal输出为1；
       equal =1;
      else      //a不等于b时，equal输出为0。
       equal = 0;  //思考：如果不写else 部分会产生什么逻辑？
endmodule
*/