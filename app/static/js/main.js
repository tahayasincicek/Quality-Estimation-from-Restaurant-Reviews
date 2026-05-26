document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();

  // Tabs
  const tabBtns = document.querySelectorAll('.tab-btn');
  tabBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      const target = btn.getAttribute('data-target');
      if (!target) return;
      // Tab group handling
      const group = btn.closest('div').parentElement;
      group.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
      group.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      document.getElementById(target).classList.add('active');
    });
  });

  // Btn Groups
  const btnGroups = document.querySelectorAll('.btn-group');
  btnGroups.forEach(group => {
    const btns = group.querySelectorAll('.btn');
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        btns.forEach(b => b.classList.remove('active'));
        btn.classList.add('active');
      });
    });
  });

  // Textarea counter
  const predictText = document.getElementById('predict-text');
  if (predictText) {
    const counter = document.getElementById('char-count');
    predictText.addEventListener('input', () => {
      counter.textContent = `${predictText.value.length} characters`;
    });
  }

  // Sample links
  const samples = document.querySelectorAll('.sample-links a');
  samples.forEach(link => {
    link.addEventListener('click', (e) => {
      const type = e.target.textContent.trim().toLowerCase();
      const txt = document.getElementById('predict-text');
      if (!txt) return;
      if (type === 'positive') txt.value = "The food was absolutely fantastic and the service was top notch. Highly recommended!";
      if (type === 'neutral') txt.value = "It was okay. The food was nothing special but the place was clean enough.";
      if (type === 'negative') txt.value = "Terrible experience. We waited an hour for cold food and the waiter was extremely rude.";
      txt.dispatchEvent(new Event('input'));
    });
  });

  // Predict
  const btnAnalyze = document.getElementById('btn-analyze');
  if (btnAnalyze) {
    btnAnalyze.addEventListener('click', async () => {
      const txt = document.getElementById('predict-text').value.trim();
      if (!txt) {
        alert("Please enter a review text.");
        return;
      }
      
      const activeModelBtn = document.querySelector('#model-select .btn.active');
      const modelName = activeModelBtn ? activeModelBtn.getAttribute('data-model') : 'lr';

      const originalHtml = btnAnalyze.innerHTML;
      btnAnalyze.disabled = true;
      btnAnalyze.innerHTML = '<i data-lucide="loader" class="spin"></i> Analyzing...';
      if (window.lucide) lucide.createIcons();

      try {
        const res = await fetch('/predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ text: txt, model_name: modelName })
        });
        const data = await res.json();
        
        if (data.error) {
          alert("Error: " + data.error);
        } else {
          document.getElementById('result-empty').style.display = 'none';
          document.getElementById('result-content').style.display = 'block';
          
          document.getElementById('res-pred').textContent = data.label.toUpperCase();
          const ind = document.getElementById('res-indicator');
          ind.className = 'result-indicator ' + data.label.toLowerCase();
          
          document.getElementById('res-time').textContent = `${data.elapsed_ms}ms`;
          
          const conf = data.confidence;
          document.getElementById('conf-poor').style.width = `${conf.poor}%`;
          document.getElementById('conf-poor-val').textContent = `${Math.round(conf.poor)}%`;
          document.getElementById('conf-avg').style.width = `${conf.average}%`;
          document.getElementById('conf-avg-val').textContent = `${Math.round(conf.average)}%`;
          document.getElementById('conf-good').style.width = `${conf.good}%`;
          document.getElementById('conf-good-val').textContent = `${Math.round(conf.good)}%`;
          
          document.getElementById('res-stats').innerHTML = `${data.stats.word_count} words &middot; ${data.stats.char_count} chars &middot; sentiment: ${data.stats.sentiment > 0 ? '+'+data.stats.sentiment : data.stats.sentiment}`;
          
          if (data.top_words) {
            const words = data.top_words.map(x => x.word);
            const scores = data.top_words.map(x => x.score);
            const chartCanvas = document.getElementById('word-impact-chart');
            if (chartCanvas && chartCanvas.parentElement) {
              chartCanvas.parentElement.style.height = '280px';
            }
            if (window.drawWordImpact) drawWordImpact('word-impact-chart', words, scores);
          }
          
          if (data.all_models) {
            const tbody = document.getElementById('all-models-tbody');
            tbody.innerHTML = '';
            data.all_models.forEach(m => {
              tbody.innerHTML += `<tr>
                <td>${m.name}</td>
                <td>${m.type}</td>
                <td><span class="badge-${m.label.toLowerCase()}">${m.label}</span></td>
                <td>${Math.round(m.conf)}%</td>
                <td>${m.time}ms</td>
              </tr>`;
            });
          }
        }
      } catch (err) {
        alert("Request failed.");
        console.error(err);
      } finally {
        btnAnalyze.disabled = false;
        btnAnalyze.innerHTML = originalHtml;
        if (window.lucide) lucide.createIcons();
      }
    });
  }

  // Comparison Sorting
  const ths = document.querySelectorAll('.sortable');
  ths.forEach(th => {
    th.addEventListener('click', () => {
      const table = th.closest('table');
      const tbody = table.querySelector('tbody');
      const rows = Array.from(tbody.querySelectorAll('tr'));
      const index = Array.from(th.parentElement.children).indexOf(th);
      const isAsc = th.classList.contains('asc');
      
      rows.sort((a, b) => {
        const valA = a.children[index].textContent.trim();
        const valB = b.children[index].textContent.trim();
        const numA = parseFloat(valA);
        const numB = parseFloat(valB);
        if (!isNaN(numA) && !isNaN(numB)) {
          return isAsc ? numA - numB : numB - numA;
        }
        return isAsc ? valA.localeCompare(valB) : valB.localeCompare(valA);
      });
      
      ths.forEach(t => t.classList.remove('asc', 'desc'));
      th.classList.add(isAsc ? 'desc' : 'asc');
      
      tbody.innerHTML = '';
      rows.forEach(r => tbody.appendChild(r));
    });
  });

  // Comparison highlighting
  const statCells = document.querySelectorAll('.stat-cell');
  statCells.forEach(cell => {
    const lbl = cell.querySelector('.stat-label');
    if (lbl && (lbl.textContent.includes('Best Model') || lbl.textContent.includes('Highest F1'))) {
      cell.classList.add('highlight');
    }
  });

  const compTable = document.querySelector('table th.sortable');
  if (compTable) {
    const table = compTable.closest('table');
    let f1Index = -1;
    table.querySelectorAll('th').forEach((th, idx) => {
      if (th.textContent.includes('F1')) f1Index = idx;
    });
    if (f1Index !== -1) {
      let maxVal = -1;
      let bestTd = null;
      table.querySelectorAll('tbody tr').forEach(tr => {
        const td = tr.children[f1Index];
        const val = parseFloat(td.textContent);
        if (!isNaN(val) && val > maxVal) { maxVal = val; bestTd = td; }
      });
      if (bestTd) bestTd.classList.add('best');
    }
  }

  // Confusion / History buttons
  const loadImgBtn = (btnSelector, imgId, baseUrl) => {
    const btns = document.querySelectorAll(btnSelector);
    btns.forEach(btn => {
      btn.addEventListener('click', () => {
        document.getElementById(imgId).src = `${baseUrl}/${btn.getAttribute('data-model')}`;
      });
    });
  };
  loadImgBtn('#cm-btns .btn', 'cm-img', '/confusion');
  loadImgBtn('#hist-btns .btn', 'hist-img', '/history');

  // Bulk input method
  const bulkMethod = document.getElementsByName('bulk-method');
  if (bulkMethod.length) {
    bulkMethod.forEach(r => r.addEventListener('change', () => {
      document.getElementById('bulk-text-wrap').style.display = r.value === 'text' ? 'block' : 'none';
      document.getElementById('bulk-csv-wrap').style.display = r.value === 'csv' ? 'block' : 'none';
    }));
  }

  // Drag and Drop CSV
  const dropZone = document.getElementById('drop-zone');
  const fileInput = document.getElementById('csv-file');
  if (dropZone) {
    dropZone.addEventListener('dragover', (e) => { e.preventDefault(); dropZone.classList.add('dragover'); });
    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));
    dropZone.addEventListener('drop', (e) => {
      e.preventDefault();
      dropZone.classList.remove('dragover');
      if (e.dataTransfer.files.length) {
        fileInput.files = e.dataTransfer.files;
        handleCsvFile(fileInput.files[0]);
      }
    });
    dropZone.addEventListener('click', () => fileInput.click());
    fileInput.addEventListener('change', () => {
      if (fileInput.files.length) handleCsvFile(fileInput.files[0]);
    });
  }

  let bulkData = [];
  function handleCsvFile(file) {
    if (typeof Papa === 'undefined') { alert('PapaParse not loaded'); return; }
    Papa.parse(file, {
      complete: function(results) {
        // Assuming first column or 'text' column
        const texts = results.data.map(r => r.text || r[0]).filter(t => t && t.trim().length > 0).slice(0, 500); // limit 500
        bulkData = texts;
        document.getElementById('drop-zone-text').innerHTML = `<b>${file.name}</b> loaded<br>${texts.length} reviews found (max 500).`;
      },
      header: true
    });
  }

  // Bulk Analyze
  const btnBulk = document.getElementById('btn-bulk');
  if (btnBulk) {
    btnBulk.addEventListener('click', async () => {
      let texts = [];
      const method = document.querySelector('input[name="bulk-method"]:checked').value;
      if (method === 'text') {
        texts = document.getElementById('bulk-text').value.split('\n').filter(t => t.trim().length > 0);
      } else {
        texts = bulkData;
      }

      if (texts.length === 0) {
        alert("No reviews to analyze."); return;
      }

      const activeModelBtn = document.querySelector('#bulk-model-select .btn.active');
      const modelName = activeModelBtn ? activeModelBtn.getAttribute('data-model') : 'lr';

      btnBulk.disabled = true;
      btnBulk.innerHTML = '<i data-lucide="loader" class="spin"></i> Processing...';
      if (window.lucide) lucide.createIcons();

      try {
        const res = await fetch('/bulk_predict', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ texts, model_name: modelName })
        });
        const data = await res.json();
        
        if (data.error) {
          alert("Error: " + data.error);
        } else {
          document.getElementById('bulk-empty').style.display = 'none';
          document.getElementById('bulk-results').style.display = 'block';
          
          let good=0, avg=0, poor=0;
          const tbody = document.getElementById('bulk-tbody');
          tbody.innerHTML = '';
          
          window.bulkExportData = data.results; // store for export

          data.results.forEach((r, i) => {
            if (r.label === 'Good') good++;
            if (r.label === 'Average') avg++;
            if (r.label === 'Poor') poor++;
            
            tbody.innerHTML += `<tr>
              <td>${i+1}</td>
              <td title="${r.text}">${r.text.length > 60 ? r.text.substring(0, 60) + '...' : r.text}</td>
              <td><span class="badge-${r.label.toLowerCase()}">${r.label}</span></td>
              <td>${Math.round(r.confidence)}%</td>
            </tr>`;
          });
          
          document.getElementById('bulk-summary').innerHTML = `Good: <b>${good}</b> &middot; Average: <b>${avg}</b> &middot; Poor: <b>${poor}</b>`;
          if (window.drawDoughnut) drawDoughnut('bulk-doughnut', [good, avg, poor]);
        }
      } catch (err) {
        alert("Request failed.");
      } finally {
        btnBulk.disabled = false;
        btnBulk.innerHTML = 'Analyze';
      }
    });
  }
  
  // Bulk Export
  const exportCsv = document.getElementById('export-csv');
  if (exportCsv) {
    exportCsv.addEventListener('click', (e) => {
      e.preventDefault();
      if (!window.bulkExportData) return;
      const csv = ['Text,Prediction,Confidence'];
      window.bulkExportData.forEach(r => {
        csv.push(`"${r.text.replace(/"/g, '""')}","${r.label}",${r.confidence}`);
      });
      const blob = new Blob([csv.join('\n')], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url; a.download = 'predictions.csv'; a.click();
    });
  }
});
