public class Test 
{ 
  static final Double foo() { 
    Double bar = 1.1; 
    return ((true) ? bar : (Double) (() -> 10.0)); 
  } 
} 
//JDK 11