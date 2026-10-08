rules = {
    "start": ["<subject> <action> <place>."],
    "subject": ["Um viajante", "Uma máquina", "Um jardim"],
    "action": ["revela", "transforma", "imagina"],
    "place": ["a cidade suspensa", "um mundo novo", "a próxima linguagem"],
}

sentences = [grammar(rules) for _ in range(8)]
for sentence in sentences:
    print(sentence)
emit("narrative.txt", "\n".join(sentences))

language = {
    "start": ["plant <kind> at <int:0:100>,<int:0:100>;"],
    "kind": ["oak", "fern", "willow"],
}
emit("example.garden", "\n".join(grammar(language) for _ in range(6)))
