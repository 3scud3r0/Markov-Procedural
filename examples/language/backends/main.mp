# O exportador comum é para a IR numérica, não um transpiler de Python inteiro.
targets = ["python", "javascript", "typescript", "c", "cpp",
           "rust", "go", "lua", "sql", "json"]

program = generate("program", {"functions": 4, "iterations": 5},
                   targets=targets, name="calculos")
print("Arquivos gerados:", ", ".join(targets))
print("Use a aba Saídas para ler e baixar os fontes.")
