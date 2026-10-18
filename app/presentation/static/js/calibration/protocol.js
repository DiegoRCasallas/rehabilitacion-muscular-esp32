export const REPETITIONS = 3;

export function buildProtocol(repetitions = REPETITIONS) {
  const steps = [
    { phase: "idle", seconds: 3, text: "Prepárate: apoya el brazo en una posición cómoda" },
    { phase: "rest", seconds: 5, text: "Relaja el músculo por completo" },
  ];
  for (let i = 1; i <= repetitions; i++) {
    steps.push({ phase: "contraction", seconds: 3,
                 text: `Contracción ${i} de ${repetitions}: ¡fuerza máxima!` });
    steps.push({ phase: "idle", seconds: 4, text: "Relaja y descansa" });
  }
  return steps;
}