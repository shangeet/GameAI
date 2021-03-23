package dk.itu.mario.engine.level;

import java.util.Random;
import java.util.*;

//Make any new member variables and functions you deem necessary.
//Make new constructors if necessary
//You must implement mutate() and crossover()


public class MyDNA extends DNA
{

	public int numGenes = 0; //number of genes

	// Use these constants to make your DNA strings.

	// Represents a gap in the floor that Mario can fall through and die.
	public static final char GAP_CHAR = 'G';
	// Represents a straight, flat section of ground.
	public static final char STRAIGHT_CHAR = 'S';
	// Represents ground with coins above it.
	public static final char COINS_CHAR = 'C';
	// Represents a set of stairs that Mario needs to jump over.
	public static final char HILL_CHAR = 'H';
	// Represents ground with monsters over it (e.g., goombas, koopas).
	public static final char MONSTERS_CHAR = 'M';

	// Return a new DNA that differs from this one in a small way.
	// Do not change this DNA by side effect; copy it, change the copy, and return the copy.
	public MyDNA mutate ()
	{
		MyDNA copy = new MyDNA();
		//YOUR CODE GOES BELOW HERE
		Character[] choices = new Character[] {'G', 'S', 'C', 'H', 'M'};

		Random rand = new Random();
		int goalIndex = rand.nextInt(this.getChromosome().length() - 2);
		if (goalIndex % 2 == 1) {
			goalIndex -= 1;
		}
		String original = this.getChromosome();
		StringBuilder ans = new StringBuilder();
		for(int i = 0; i < original.length(); i+=2) {
			if (i == goalIndex) {
				ans.append(choices[rand.nextInt(5)]);
				ans.append(rand.nextInt(9) + 1);
			} else {
				ans.append(original.charAt(i));
				ans.append(original.charAt(i + 1));
			}
		}
		copy.setChromosome(ans.toString());
		//YOUR CODE GOES ABOVE HERE
		return copy;
	}

	// Do not change this DNA by side effect
	public ArrayList<MyDNA> crossover (MyDNA mate)
	{
		ArrayList<MyDNA> offspring = new ArrayList<MyDNA>();
		Random rand = new Random();
		//YOUR CODE GOES BELOW HERE
		//uniform crossover is superior muhahahahaha
		MyDNA childA = new MyDNA();
		MyDNA childB = new MyDNA();
		StringBuilder A = new StringBuilder();
		StringBuilder B = new StringBuilder();
		//String A = this.getChromosome().substring(0, 100) + mate.getChromosome().substring(100);
		//String B = this.getChromosome().substring(100) + mate.getChromosome().substring(0, 100);
        for(int i = 0; i < mate.getChromosome().length(); i+=2) {
            double swag = rand.nextDouble();
            if (swag > 0.5) {
                A.append(mate.getChromosome().charAt(i) + this.getChromosome().charAt(i + 1));
                B.append(this.getChromosome().charAt(i) + mate.getChromosome().charAt(i + 1));
            } else {
                B.append(mate.getChromosome().charAt(i) + this.getChromosome().charAt(i + 1));
                A.append(this.getChromosome().charAt(i) + mate.getChromosome().charAt(i + 1));
            }
        }

		childA.setChromosome(A.toString());
		childA.setNumGenes(200);
		childB.setChromosome(B.toString());
		childB.setNumGenes(200);

		//YOUR CODE GOES ABOVE HERE
		return offspring;
	}

	// Optional, modify this function if you use a means of calculating fitness other than using the fitness member variable.
	// Return 0 if this object has the same fitness as other.
	// Return -1 if this object has lower fitness than other.
	// Return +1 if this objet has greater fitness than other.
	public int compareTo(MyDNA other)
	{
		int result = super.compareTo(other);
		return result;
	}


	// For debugging purposes (optional)
	public String toString ()
	{
		String s = super.toString();
		//YOUR CODE GOES BELOW HERE
		String A =  this.getChromosome();
		String B = Integer.toString(this.numGenes);
		String C = Double.toString(this.getFitness());
		s = A + " | " + B + " | " + C;
		//YOUR CODE GOES ABOVE HERE
		return s;
	}

	public void setNumGenes (int n)
	{
		this.numGenes = n;
	}

}

