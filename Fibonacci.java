public class Fibonacci {
  public static void main(String[] args) {

    int num = 15;
    int a = 0, b = 1;

    System.out.print(a + " , " + b + " , ");

    int nextNumber;

    for (int i = 2; i < num; i++) {
      nextNumber = a + b;
      a = b;
      b = nextNumber;
      System.out.print(nextNumber + " , ");
    }

  }
}
