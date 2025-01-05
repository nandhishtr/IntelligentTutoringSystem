import random
from deap import base, creator, tools
import json

# Load questions from a JSON file
def load_questions(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

# Calculates the fitness of an individual (a set of questions) based on user performance
# and question diversity. It rewards questions based on user performance and penalizes
# repeated topics.
def evaluate(individual, user_performance):
    """Fitness function that evaluates individuals based on user performance and diversity."""
    fitness = 0
    seen_topics = set()

    for question in individual:
        # Reward based on user performance for the topic
        topic_fitness = user_performance.get(question["Topic"], 1)
        difficulty_score = {"Easy": 1, "Medium": 2, "Hard": 3}.get(question["Difficulty"], 1)
        fitness += topic_fitness * difficulty_score

        # Penalize repeated topics
        if question["Topic"] in seen_topics:
            fitness -= 1  # Reduce fitness for repeated topics
        seen_topics.add(question["Topic"])

    return (fitness,)


def adaptive_quiz_ga(questions, user_performance, num_questions=10, generations=50, population_size=20):
    """Genetic algorithm for selecting quiz questions."""
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)

    toolbox = base.Toolbox()
    toolbox.register("attr_question", lambda: random.choice(questions))
    toolbox.register("individual", tools.initRepeat, creator.Individual, toolbox.attr_question, n=num_questions)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    # Define genetic operators
    toolbox.register("evaluate", evaluate, user_performance=user_performance)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.2)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # Initialize population with unique questions
    population = toolbox.population(n=population_size)

    # Evolution process
    for gen in range(generations):
        # Evaluate fitness
        fitnesses = list(map(toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit

        # Apply elitism to preserve the best individual
        best_individual = tools.selBest(population, 1)[0]
        offspring = toolbox.select(population, len(population) - 1)
        offspring = list(map(toolbox.clone, offspring))

        # Apply crossover and mutation
        for child1, child2 in zip(offspring[::2], offspring[1::2]):
            if random.random() < 0.7 and len(child1) > 1 and len(child2) > 1:
                toolbox.mate(child1, child2)
                del child1.fitness.values, child2.fitness.values
        for mutant in offspring:
            if random.random() < 0.2 and len(mutant) > 1:
                toolbox.mutate(mutant)
                del mutant.fitness.values

        # Add the best individual back to the population
        offspring.append(best_individual)
        population[:] = offspring

    # Return the best individual
    best_individual = tools.selBest(population, 1)[0]
    return best_individual

def run_quiz(questions, num_questions=10):
    user_performance = {}
    asked_questions = []

    print("Welcome to the adaptive German vocabulary quiz!")

    correct_answers = 0
    for i in range(num_questions):
        # Run the genetic algorithm to pick the next quiz
        best_quiz = adaptive_quiz_ga(questions, user_performance, num_questions=1)
        question = best_quiz[0]

        # Display the question
        print(f"\nQuestion {i + 1}: {question['Question']}")
        for idx, choice in enumerate(question["Choices"], 1):
            print(f"{idx}. {choice}")

        # User's answer
        user_answer = input("Your answer (1-4): ").strip()
        try:
            user_choice = int(user_answer)
            selected_answer = question["Choices"][user_choice - 1]
        except (ValueError, IndexError):
            print("Invalid choice. Moving to the next question.")
            continue

        # Evaluate the answer
        if selected_answer == question["CorrectAnswer"]:
            print("Correct!")
            user_performance[question["Topic"]] = user_performance.get(question["Topic"], 1) + 1
            correct_answers += 1
        else:
            print(f"Wrong! The correct answer was: {question['CorrectAnswer']}")
            user_performance[question["Topic"]] = max(1, user_performance.get(question["Topic"], 1) - 1)

        # Track asked questions
        asked_questions.append(question)

    print(f"\nQuiz completed! You answered {correct_answers} correctly out of {num_questions}.")

def main():
    questions_file = "quiz_questions.json"
    questions = load_questions(questions_file)

    run_quiz(questions, num_questions=10)

if __name__ == "__main__":
    main()
