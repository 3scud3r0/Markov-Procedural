# Não precisa gerar uma cena. É programação de propósito geral.
import json
from collections import Counter

class Sequence:
    def __init__(self, size):
        self.size = size

    def fibonacci(self):
        a, b = 0, 1
        result = []
        for _ in range(self.size):
            result.append(a)
            a, b = b, a + b
        return result

length = param("length", 20, min=2, max=80, step=1)
values = Sequence(length).fibonacci()
frequencies = dict(Counter(str(value)[-1] for value in values))
print("Fibonacci:", values)
print("Frequência do último dígito:", frequencies)
emit("fibonacci.json", {"values": values, "frequencies": frequencies})
emit("fibonacci.csv", "index,value\n" + "\n".join(
    f"{index},{value}" for index, value in enumerate(values)))
