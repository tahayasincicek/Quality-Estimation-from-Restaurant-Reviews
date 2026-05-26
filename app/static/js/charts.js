let activeCharts = {};
let chartConfigs = {};

function getCssVar(name) {
  return getComputedStyle(document.documentElement).getPropertyValue(name).trim();
}

function getChartDefaults() {
  return {
    fgMuted: getCssVar('--fg-muted') || '#666',
    border: getCssVar('--border') || '#eaeaea',
    danger: getCssVar('--danger') || '#ee0000',
    success: getCssVar('--success') || '#0a0',
    warning: getCssVar('--warning') || '#f50',
    accent: getCssVar('--accent') || '#0070f3',
    fg: getCssVar('--fg') || '#000'
  };
}

function initChartGlobal() {
  if (typeof Chart !== 'undefined') {
    const c = getChartDefaults();
    Chart.defaults.font.family = 'Inter, system-ui, sans-serif';
    Chart.defaults.font.size = 13;
    Chart.defaults.color = c.fgMuted;
    Chart.defaults.layout = { padding: { top: 8, bottom: 8 } };
    Chart.defaults.plugins.tooltip.backgroundColor = 'rgba(0,0,0,0.8)';
    Chart.defaults.plugins.tooltip.titleFont = { size: 13, family: 'Inter' };
    Chart.defaults.plugins.tooltip.bodyFont = { size: 13, family: 'Inter' };
    Chart.defaults.plugins.tooltip.cornerRadius = 4;
    Chart.defaults.plugins.legend.labels.boxWidth = 10;
  }
}

function destroyChart(id) {
  if (activeCharts[id]) {
    activeCharts[id].destroy();
    delete activeCharts[id];
  }
}

window.drawWordImpact = function(canvasId, words, scores) {
  chartConfigs[canvasId] = { fn: window.drawWordImpact, args: [canvasId, words, scores] };
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const c = getChartDefaults();
  const colors = scores.map(s => s > 0 ? '#0070f3' : '#ee0000');
  
  const drawValues = {
    id: 'drawValues',
    afterDraw(chart) {
      const { ctx } = chart;
      ctx.font = '12px Inter';
      ctx.textBaseline = 'middle';
      chart.data.datasets.forEach((dataset, i) => {
        const meta = chart.getDatasetMeta(i);
        meta.data.forEach((bar, index) => {
          const val = dataset.data[index];
          if(val > 0) {
             ctx.textAlign = 'right';
             ctx.fillStyle = '#fff';
             ctx.fillText(val.toFixed(1), bar.x - 6, bar.y);
          } else {
             ctx.textAlign = 'left';
             ctx.fillStyle = '#fff';
             ctx.fillText(val.toFixed(1), bar.x + 6, bar.y);
          }
        });
      });
    }
  };

  activeCharts[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: {
      labels: words,
      datasets: [{ data: scores, backgroundColor: colors, barThickness: 16, borderRadius: 3, borderWidth: 0 }]
    },
    plugins: [drawValues],
    options: {
      indexAxis: 'y',
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: { display: false },
        y: { grid: { display: true, color: c.border, drawBorder: false }, border: { display: false }, ticks: { font: { size: 13 } } }
      }
    }
  });
}

window.drawGroupedBar = function(canvasId, labels, datasetsData, seriesNames) {
  chartConfigs[canvasId] = { fn: window.drawGroupedBar, args: [canvasId, labels, datasetsData, seriesNames] };
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const c = getChartDefaults();
  const colors = ['#0070f3','#6366f1','#8b5cf6','#06b6d4','#10b981'];
  
  const datasets = datasetsData.map((data, i) => ({
    label: seriesNames[i],
    data: data,
    backgroundColor: colors[i % colors.length],
    barThickness: 18,
    borderWidth: 0,
    borderRadius: 4
  }));

  activeCharts[canvasId] = new Chart(ctx, {
    type: 'bar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { 
        legend: { position: 'top', align: 'start', labels: { font: { size: 12 } } },
        tooltip: {
          callbacks: {
            label: function(context) {
              return context.dataset.label + ': ' + (context.raw * 100).toFixed(1) + '%';
            }
          }
        }
      },
      scales: {
        x: { grid: { display: false }, border: { display: false } },
        y: { 
          grid: { color: c.border }, border: { display: false }, 
          min: 0, max: 1,
          ticks: {
            callback: function(value) { return (value * 100) + '%'; }
          }
        }
      }
    }
  });
}

window.drawRadar = function(canvasId, labels, datasetsData, seriesNames) {
  chartConfigs[canvasId] = { fn: window.drawRadar, args: [canvasId, labels, datasetsData, seriesNames] };
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const c = getChartDefaults();
  const colors = ['#0070f3','#6366f1','#8b5cf6','#06b6d4','#10b981'];
  
  const datasets = datasetsData.map((data, i) => ({
    label: seriesNames[i],
    data: data,
    backgroundColor: colors[i % colors.length] + '14', 
    borderColor: colors[i % colors.length],
    borderWidth: 2,
    pointRadius: 4,
    pointHoverRadius: 6,
    fill: true
  }));

  activeCharts[canvasId] = new Chart(ctx, {
    type: 'radar',
    data: { labels, datasets },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      scales: { 
        r: { 
          grid: { color: c.border }, 
          angleLines: { color: c.border }, 
          pointLabels: { font: { size: 12 } }, 
          ticks: { display: false, maxTicksLimit: 3 },
          min: 0, max: 1
        } 
      }
    }
  });
}

window.drawDoughnut = function(canvasId, data) {
  chartConfigs[canvasId] = { fn: window.drawDoughnut, args: [canvasId, data] };
  destroyChart(canvasId);
  const ctx = document.getElementById(canvasId);
  if (!ctx) return;
  const c = getChartDefaults();
  
  const total = data.reduce((a, b) => a + b, 0);
  
  const centerText = {
    id: 'centerText',
    afterDraw(chart) {
      const { ctx, width, height } = chart;
      ctx.restore();
      ctx.font = "600 24px Inter";
      ctx.textBaseline = "middle";
      ctx.textAlign = "center";
      ctx.fillStyle = c.fg;
      const textX = width / 2;
      const textY = height / 2 - 10;
      ctx.fillText(total.toString(), textX, textY);
      
      ctx.font = "12px Inter";
      ctx.fillStyle = c.fgMuted;
      ctx.fillText("Total", textX, textY + 22);
      ctx.save();
    }
  };

  activeCharts[canvasId] = new Chart(ctx, {
    type: 'doughnut',
    data: {
      labels: ['Good', 'Average', 'Poor'],
      datasets: [{ 
        data, 
        backgroundColor: ['#10b981', '#f59e0b', '#ef4444'], 
        borderWidth: 0,
        borderRadius: 4,
        hoverOffset: 4
      }]
    },
    plugins: [centerText],
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: '70%',
      plugins: { legend: { display: false } }
    }
  });
}

document.addEventListener('themeChange', () => {
  initChartGlobal();
  const configs = { ...chartConfigs };
  for (let id in activeCharts) {
    destroyChart(id);
  }
  activeCharts = {};
  for(let id in configs) {
    configs[id].fn(...configs[id].args);
  }
});

document.addEventListener('DOMContentLoaded', initChartGlobal);
