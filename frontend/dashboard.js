/* eslint-disable no-undef */
const fairCtx = document.getElementById('fairChart').getContext('2d');
let chart;

function renderChart(samples = []) {
  if (chart) chart.destroy();
  chart = new Chart(fairCtx, {
    type: 'bar',
    data: {
      labels: samples.map((_, idx) => idx + 1),
      datasets: [
        {
          label: 'Simulated Loss',
          data: samples,
          backgroundColor: '#4a90e2',
        },
      ],
    },
    options: {
      plugins: { legend: { display: false } },
      scales: {
        y: {
          beginAtZero: true,
          title: { display: true, text: 'AUD$' },
        },
        x: { display: false },
      },
    },
  });
}

function showE8(result) {
  const target = document.getElementById('e8-output');
  target.textContent = JSON.stringify(result, null, 2);
}

function showFair(result) {
  const target = document.getElementById('fair-output');
  target.textContent = JSON.stringify(result, null, 2);
  renderChart(result.monte_carlo_samples || []);
}

window.showE8 = showE8;
window.showFair = showFair;
