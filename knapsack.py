import itertools, functools
from typing import Sequence
import time
import matplotlib.pyplot as plt

# Clase para construir nuestros experimentos
class Experiment:
    def __init__(self, trials):
        self.trials = trials

        self.currentStep = 1
        self.increment = 1

        self.timesPerStepBFS = []
        self.avgTimesPerStepBFS = []

        self.timesPerStepAStar = []
        self.avgTimesPerStepAStar = []
    
    def runStepAStar(self, step):
        print("\n# STEP " + str(self.currentStep))
        times = []
        for x in range(self.trials):
            start = time.time()

            # TODO: Insertar codigo
            ex = Knapsack(step)
            bestKnapsack = ex.solveAStar()
            print(ex.calculateError(bestKnapsack), ex.knapsackWeight(bestKnapsack), ex.knapsackProfit(bestKnapsack), bestKnapsack)

            end = time.time()
            currentTime = (end - start) * 1000
            times.append(currentTime)
            print("\n# TRIAL " + str(x) + " took " + str(currentTime) + " s")
        avgTime = sum(times) / len(times)
        self.timesPerStepAStar.append(times)
        self.avgTimesPerStepAStar.append(avgTime)

        print("\n\n# STEP TIMES:", times, "AVG: " + str(avgTime) + " s")

    def runStepBFS(self, step):
        print("\n# STEP " + str(self.currentStep))
        times = []
        for x in range(self.trials):
            start = time.time()

            # TODO: Insertar codigo
            ex = Knapsack(step)
            bestKnapsack = ex.solveBFS()
            print(ex.calculateError(bestKnapsack), ex.knapsackWeight(bestKnapsack), ex.knapsackProfit(bestKnapsack), bestKnapsack)

            end = time.time()
            currentTime = (end - start) * 1000
            times.append(currentTime)
            print("\n# TRIAL " + str(x) + " took " + str(currentTime) + " s")
        avgTime = sum(times) / len(times)
        self.timesPerStepBFS.append(times)
        self.avgTimesPerStepBFS.append(avgTime)

        print("\n\n# STEP TIMES:", times, "AVG: " + str(avgTime) + " s")

    def run(self, steps, increment=1):
        self.increment = increment
        self.steps = steps
        for step in steps:
            self.runStepAStar(step)
            self.runStepBFS(step)
            self.currentStep += 1

    def plot(self):
        # rows = 1
        # fig, ax = plt.subplots(rows, len(self.steps), sharey=True, sharex=True)

        # for step in range(self.trials):
        #     ax[step].bar([str(trial) for trial in range(self.increment, len(self.steps) * self.increment, self.increment)], self.timesPerStep[step])
            # ax[0, step].bar([str(trial) for trial in range(self.increment, (self.steps + 1) * self.increment, self.increment)], self.timesPerStep[step])
            # ax[0, step].set_title(str((step + 1) * self.increment) + " nodos")
            # ax[1, step].bar([str(trial) for trial in range(self.increment, (self.steps + 1) * self.increment, self.increment)], self.timesPerStepDirected[step])
            # ax[0, step].set_title(str((step + 1) * self.increment) + " nodos")

        # fig.text(0.5, 0.04, 'Numero de Nodos', ha='center', va='center')
        # fig.text(0.06, 0.5, 'Tiempo de Ejecucion (ms)', ha='center', va='center', rotation='vertical')
        # fig.suptitle('Tiempos de Ejecucion de algoritmo de Djikstra')
        # plt.show()

        plt.plot([step.split("/")[1] for step in self.steps], self.avgTimesPerStepAStar, label="Busqueda A*")
        plt.plot([step.split("/")[1] for step in self.steps], self.avgTimesPerStepBFS, label="Busqueda por Amplitud")

        plt.xlabel("Problema")
        plt.ylabel("Tiempo de Ejecucion Promedio (s)")
        plt.legend()
        plt.show()

class Knapsack:
    def __init__(self, problemPath: str) -> None:
        with open(f'./problems/{problemPath}') as file:
            parsedLines = [dict(zip(('profit', 'weight'), map(float, line.strip().split(" ")))) for line in file.readlines()]
            head = parsedLines.pop(0)

            self.n = head['profit']
            self.wmax = head['weight']
            self.items = parsedLines

        folder, file = problemPath.split("/")
        optimumPath = folder + "-optimum/" + file 
        with open(f'./problems/{optimumPath}') as file:
            self.optimum = float(file.readline().strip())

        # print(self.n, self.wmax, self.items, [x['weight'] for x in self.items])

    def knapsackWeight(self, knapsack: Sequence) -> float:
        if len(knapsack) > 1:
            return functools.reduce(lambda knapsackWeight, item: knapsackWeight + item['weight'], knapsack, 0)
        elif len(knapsack) == 1:
            return knapsack[0]['weight']
        else:
            return 0

    def knapsackProfit(self, knapsack: Sequence) -> float:
        if len(knapsack) > 1:
            return functools.reduce(lambda knapsackProfit, item: knapsackProfit + item['profit'], knapsack, 0)
        elif len(knapsack) == 1:
            return knapsack[0]['profit']
        else:
            return 0

    def clipKnapsack(self, knapsack: Sequence) -> list:
        clippedKnapsack = []
        clippedKnapsackWeight = 0
        for item in knapsack:
            newWeight = clippedKnapsackWeight + item['weight']
            if newWeight <= self.wmax:
                clippedKnapsackWeight = newWeight
                clippedKnapsack.append(item)
        return clippedKnapsack

    def verifySolution(self, knapsack) -> bool:
        return self.knapsackProfit(knapsack) == self.optimum

    def calculateError(self, knapsack) -> float:
        return (self.knapsackProfit(knapsack) / self.optimum) * 100

    def solveBFS(self) -> list:
        pool = tuple(self.items)
        n = len(pool)
        knapsacks = []
        for indices in itertools.product(range(n), repeat=n):
            if len(set(indices)) == n:
                knapsack = self.clipKnapsack(tuple(pool[i] for i in indices))
                knapsacks.append(knapsack)
        
        knapsacks.sort(key=lambda knapsack: self.knapsackProfit(knapsack), reverse=True)
        return knapsacks[0]

    def solveAStar(self) -> list:
        def heuristic(item):
            try:
                return (item['profit'] / item['weight'])
            except:
                return 0

        self.items.sort(key=lambda item: heuristic(item) + item['weight'])

        currentKnapsack = []
        for item in self.items:
            if self.knapsackWeight(currentKnapsack) + item['weight'] <= self.wmax:
                currentKnapsack.append(item)

        # print(self.optimum, self.knapsackProfit(currentKnapsack), currentKnapsack)
        return currentKnapsack

# ex = Knapsack("large_scale/knapPI_3_10000_1000_1")
# ex = Knapsack("large_scale/knapPI_1_100_1000_1")
# ex = Knapsack("low-dimensional/f6_l-d_kp_10_60")
# ex = Knapsack("low-dimensional/f5_l-d_kp_15_375")
# bestKnapsack = ex.solveAStar()
# print(ex.calculateError(bestKnapsack))
# if ex.verifySolution(bestKnapsack):
#     print("Optimum ->", ex.knapsackWeight(bestKnapsack), ex.knapsackProfit(bestKnapsack), bestKnapsack)


# # Ahora a correr el experimento de 20 en 20 hasta 100
ex2 = Experiment(1)
# # Correr 5 pruebas por cada tipo de grafo y numero de nodos
ex2.run(["low-dimensional/f4_l-d_kp_4_11", "low-dimensional/f3_l-d_kp_4_20", "low-dimensional/f6_l-d_kp_10_60", "low-dimensional/f7_l-d_kp_7_50", "low-dimensional/f9_l-d_kp_5_80", "low-dimensional/f8_l-d_kp_23_10000"], increment=1)
# # Construir y mostrar las graficas con los resultados del experimento
ex2.plot()
