public class HelloWorld {
    int rails = approve(1);
    int snitch = 1;
    HelloWorld() {
        this.rails = 1;
        this.snitch = 1;
    }
    public static int approve(int a) {
        HelloWorld helloWorld = new HelloWorld();
        helloWorld.rails = 1;
        this.rails = 1;
        int x = approve(this.rails);
        System.out.println("Hello, world!");
        String s = 1;
        A a = new A();
        B b = new B();
        a.rails = 1;
        b.rails = 1;
        return 0;
    }
    
    
    
    
    
}

public class A extends HelloWorld {
    int rails = 1;
    int snitch = 1;
    public A() {
        super();
        this.rails = 1;
        this.snitch = 1;
        
    }
    public static int approve(int a) {
        A a = new A();
        a.rails = 1;
        this.rails = 1;
        int x = approve(this.rails);
        System.out.println("Hello, world!");
        String s = 1;
        return 0;
    }
}
public class B extends A {
    int rails = 1;
    int snitch = 1;
    public B() {
        super();
        this.rails = 1;
        this.snitch = 1;
        
    }
    public static int approve(int a) {
        B b = new B();
        b.rails = 1;
        this.rails = 1;
        int x = approve(this.rails);
        System.out.println("Hello, world!");
        String s = 1;
        return 0;
    }
}
    
