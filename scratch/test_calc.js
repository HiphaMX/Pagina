const matches = [
  { id: 1, phase: 'grupo', teamA: 'arb', teamB: 'neg', scoreA: 2, scoreB: 1, status: 'finished' },
  { id: 2, phase: 'grupo', teamA: 'hab', teamB: 'tat', scoreA: null, scoreB: null, status: 'active' },
  { id: 3, phase: 'grupo', teamA: 'ser', teamB: 'arb', scoreA: null, scoreB: null, status: 'active' }
];

const chizkoVotes = { "1": "A", "2": "B", "3": "B" };
const weroVotes = { "1": "A" };
const andreaVotes = {};

function calculatePointsForParticipant(userVotes) {
  let points = 0;
  matches.forEach(m => {
    if (m.status !== 'finished') return;
    const vote = userVotes[m.id];
    if (!vote) return;
    
    // Regla de empate (draw)
    const isDraw = m.scoreA !== null && m.scoreB !== null && m.scoreA === m.scoreB;
    if (isDraw) {
      if (m.phase === 'grupo') {
        points += 1;
      }
      return;
    }

    const winner = m.scoreA > m.scoreB ? 'A' : (m.scoreB > m.scoreA ? 'B' : null);
    if (winner === null) return;
    if (m.phase === 'grupo') {
      if (vote === winner) {
        points += 3;
      } else {
        points -= 1;
      }
    } else if (m.phase === 'semifinal') {
      if (vote === winner) {
        points += 6;
      } else {
        points -= 1;
      }
    } else if (m.phase === 'final') {
      if (vote === winner) {
        points += 9;
      }
    }
  });
  return Math.max(0, points);
}

console.log("Chizko points:", calculatePointsForParticipant(chizkoVotes));
console.log("Wero points:", calculatePointsForParticipant(weroVotes));
console.log("Andrea points:", calculatePointsForParticipant(andreaVotes));
