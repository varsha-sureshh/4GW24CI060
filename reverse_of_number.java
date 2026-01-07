import java.util.Scanner;
public class reverse_of_number
{
    public static void main (String[] args)
    {
        Scanner sc=new Scanner(System.in);
        System.out.print("enter a number:");
        int number=sc.nextInt();
        System.out.print("reverse of" + number + "is");
        int reverse =0;
        String s="";
        while(number!=0)
        {
            int pick_last=number%10;
            s=s+Integer.toString(pick_last);
    
        }
    System.out.print(s);
    sc.close();
    }
}