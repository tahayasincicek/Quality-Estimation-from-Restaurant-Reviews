document.addEventListener('DOMContentLoaded', () => {
  if (window.lucide) lucide.createIcons();

  // ============================================
  // SPA ROUTER
  // ============================================
  function initRouter() {
    const navLinks = document.querySelectorAll('.sidebar .nav-item');
    
    document.body.addEventListener('click', async (e) => {
      const link = e.target.closest('.sidebar .nav-item');
      if (link) {
        e.preventDefault();
        const url = link.getAttribute('href');
        
        if (url === window.location.pathname) return; 
        
        navLinks.forEach(n => n.classList.remove('active'));
        link.classList.add('active');

        await navigateTo(url);
      }
    });

    window.addEventListener('popstate', async () => {
      navLinks.forEach(n => {
        n.classList.remove('active');
        if (n.getAttribute('href') === window.location.pathname) n.classList.add('active');
      });
      await navigateTo(window.location.pathname, false);
    });
  }

  async function navigateTo(url, push = true) {
    const mainContent = document.querySelector('.main-content');
    mainContent.style.opacity = '0.5';

    try {
      const response = await fetch(url);
      if (!response.ok) throw new Error('Fetch error');
      const htmlText = await response.text();
      
      const parser = new DOMParser();
      const doc = parser.parseFromString(htmlText, 'text/html');
      
      const newMain = doc.querySelector('.main-content');
      
      if (newMain) {
        mainContent.innerHTML = newMain.innerHTML;
        if (push) {
          window.history.pushState({}, '', url);
        }
        
        if (window.lucide) lucide.createIcons();
        initPageEvents();
      } else {
        window.location.href = url; 
      }
    } catch (error) {
      console.error('Routing failed:', error);
      window.location.href = url; 
    } finally {
      mainContent.style.opacity = '1';
    }
  }


  // ============================================
  // PAGE EVENTS (Called after every route change)
  // ============================================
  function initPageEvents() {

    // Tabs
    const tabBtns = document.querySelectorAll('.tab-btn');
    tabBtns.forEach(btn => {
      btn.addEventListener('click', () => {
        const target = btn.getAttribute('data-target');
        if (!target) return;
        const group = btn.closest('div').parentElement;
        group.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
        group.querySelectorAll('.tab-pane').forEach(p => p.classList.remove('active'));
        btn.classList.add('active');
        const tgt = document.getElementById(target);
        if(tgt) tgt.classList.add('active');
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
        if(counter) counter.textContent = `${predictText.value.length} characters`;
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
        if (type === 'sarcastic') txt.value = "Oh brilliant! I absolutely loved waiting two hours for a cold, flavorless soup. Best experience of my life, truly a masterpiece of disaster.";
        if (type === 'mixed') txt.value = "The food was completely raw and awful, but I honestly loved the live music and the waitstaff was incredibly sweet and fast.";
        if (type === 'negation') txt.value = "I cannot say that the food was bad, and it wasn't the worst service either, but it definitely didn't fail to disappoint me today.";
        txt.dispatchEvent(new Event('input'));
      });
    });

    // Predict
    const btnAnalyze = document.getElementById('btn-analyze');
    if (btnAnalyze) {
      let datasetUsefulVotes = null;

      const btnRandomReview = document.getElementById('btn-random-review');
      const statsSpan = document.getElementById('current-reviewer-stats');
      
      const newBtnRandom = btnRandomReview ? btnRandomReview.cloneNode(true) : null;
      if (newBtnRandom && btnRandomReview.parentNode) {
        btnRandomReview.parentNode.replaceChild(newBtnRandom, btnRandomReview);
        newBtnRandom.addEventListener('click', async () => {
          try {
            const res = await fetch('/random_dataset_review');
            const data = await res.json();
            if (data && data.text) {
              const txtInput = document.getElementById('predict-text');
              if(txtInput) {
                txtInput.value = data.text;
                txtInput.dispatchEvent(new Event('input'));
              }
              datasetUsefulVotes = data.useful;
              if(statsSpan) {
                statsSpan.style.display = 'inline';
                statsSpan.textContent = `Review 'Useful' Votes: ${data.useful}`;
              }
            }
          } catch (e) {
            console.error("Error fetching random review", e);
          }
        });
      }

      const newBtnAnalyze = btnAnalyze.cloneNode(true);
      if(btnAnalyze.parentNode) {
         btnAnalyze.parentNode.replaceChild(newBtnAnalyze, btnAnalyze);
         newBtnAnalyze.addEventListener('click', async () => {
          const txtInput = document.getElementById('predict-text');
          if(!txtInput) return;
          const txt = txtInput.value.trim();
          if (!txt) {
            alert("Please enter a review text.");
            return;
          }
          
          const activeModelBtn = document.querySelector('#model-select .btn.active');
          const modelName = activeModelBtn ? activeModelBtn.getAttribute('data-model') : 'lr';

          const originalHtml = newBtnAnalyze.innerHTML;
          newBtnAnalyze.disabled = true;
          newBtnAnalyze.innerHTML = '<i data-lucide="loader" class="spin"></i> Analyzing...';
          if (window.lucide) lucide.createIcons();

          try {
            const res = await fetch('/predict', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ text: txt, model_name: modelName, useful_votes: datasetUsefulVotes })
            });
            const data = await res.json();
            
            if (data.error) {
              alert("Error: " + data.error);
            } else {
              document.getElementById('result-empty').style.display = 'none';
              document.getElementById('result-content').style.display = 'block';
              
              const sarcasmAlert = document.getElementById('sarcasm-alert');
              if (sarcasmAlert) {
                sarcasmAlert.style.display = data.is_sarcastic ? 'block' : 'none';
              }
              
              const profilerSpamAlert = document.getElementById('profiler-alert-spam');
              const profilerTrustedAlert = document.getElementById('profiler-alert-trusted');
              if (profilerSpamAlert && profilerTrustedAlert) {
                  profilerSpamAlert.style.display = 'none';
                  profilerTrustedAlert.style.display = 'none';
                  
                  if (data.reviewer_profile) {
                      if (data.reviewer_profile.is_spam_risk) {
                          profilerSpamAlert.style.display = 'block';
                          document.getElementById('profiler-spam-msg').textContent = data.reviewer_profile.warning_message;
                      } else if (data.reviewer_profile.is_trusted) {
                          profilerTrustedAlert.style.display = 'block';
                          document.getElementById('profiler-trusted-msg').textContent = data.reviewer_profile.badge_message;
                      }
                  }
              }
              
              const aspectContainer = document.getElementById('aspect-insights-container');
              const aspectContent = document.getElementById('aspect-insights-content');
              if (aspectContainer && aspectContent) {
                if (data.aspect_insights && data.aspect_insights.length > 0) {
                  aspectContainer.style.display = 'block';
                  aspectContent.innerHTML = '';
                  data.aspect_insights.forEach(item => {
                     let badgeClass = item.sentiment === 'Good' ? 'badge-good' : (item.sentiment === 'Poor' ? 'badge-poor' : 'badge-average');
                     let tooltip = item.sentences.join(' | ').replace(/"/g, '&quot;');
                     aspectContent.innerHTML += `<div style="display: flex; justify-content: space-between; align-items: center; padding: 4px 0;" title="${tooltip}">
                        <span style="font-weight: 500; font-size: 14px;">${item.aspect}</span>
                        <span class="${badgeClass}" style="font-size: 12px; padding: 2px 6px;">${item.sentiment}</span>
                     </div>`;
                  });
                } else {
                  aspectContainer.style.display = 'none';
                }
              }
              
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
            newBtnAnalyze.disabled = false;
            newBtnAnalyze.innerHTML = originalHtml;
            if (window.lucide) lucide.createIcons();
          }
        });
      }
    }

    // Comparison Sorting
    const ths = document.querySelectorAll('.sortable');
    ths.forEach(th => {
      const newTh = th.cloneNode(true);
      if(th.parentNode) {
        th.parentNode.replaceChild(newTh, th);
        newTh.addEventListener('click', () => {
          const table = newTh.closest('table');
          const tbody = table.querySelector('tbody');
          const rows = Array.from(tbody.querySelectorAll('tr'));
          const index = Array.from(newTh.parentElement.children).indexOf(newTh);
          const isAsc = newTh.classList.contains('asc');
          
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
          
          table.querySelectorAll('.sortable').forEach(t => t.classList.remove('asc', 'desc'));
          newTh.classList.add(isAsc ? 'desc' : 'asc');
          
          tbody.innerHTML = '';
          rows.forEach(r => tbody.appendChild(r));
        });
      }
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
        const newBtn = btn.cloneNode(true);
        if(btn.parentNode) {
          btn.parentNode.replaceChild(newBtn, btn);
          newBtn.addEventListener('click', () => {
            const img = document.getElementById(imgId);
            if(img) img.src = `${baseUrl}/${newBtn.getAttribute('data-model')}`;
          });
        }
      });
    };
    loadImgBtn('#cm-btns .btn', 'cm-img', '/confusion');
    loadImgBtn('#hist-btns .btn', 'hist-img', '/history');

    // Bulk input method
    const bulkMethod = document.getElementsByName('bulk-method');
    if (bulkMethod.length) {
      bulkMethod.forEach(r => {
        const newR = r.cloneNode(true);
        if(r.parentNode) {
          r.parentNode.replaceChild(newR, r);
          newR.addEventListener('change', () => {
            document.getElementById('bulk-text-wrap').style.display = newR.value === 'text' ? 'block' : 'none';
            document.getElementById('bulk-csv-wrap').style.display = newR.value === 'csv' ? 'block' : 'none';
          });
        }
      });
    }

    // Drag and Drop CSV
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('csv-file');
    if (dropZone && fileInput) {
      const newDrop = dropZone.cloneNode(true);
      const newFile = fileInput.cloneNode(true);
      dropZone.parentNode.replaceChild(newDrop, dropZone);
      fileInput.parentNode.replaceChild(newFile, fileInput);

      newDrop.addEventListener('dragover', (e) => { e.preventDefault(); newDrop.classList.add('dragover'); });
      newDrop.addEventListener('dragleave', () => newDrop.classList.remove('dragover'));
      newDrop.addEventListener('drop', (e) => {
        e.preventDefault();
        newDrop.classList.remove('dragover');
        if (e.dataTransfer.files.length) {
          newFile.files = e.dataTransfer.files;
          handleCsvFile(newFile.files[0]);
        }
      });
      newDrop.addEventListener('click', () => newFile.click());
      newFile.addEventListener('change', () => {
        if (newFile.files.length) handleCsvFile(newFile.files[0]);
      });
    }

    let bulkData = [];
    function handleCsvFile(file) {
      if (typeof Papa === 'undefined') { alert('PapaParse not loaded'); return; }
      Papa.parse(file, {
        complete: function(results) {
          const texts = results.data.map(r => r.text || r[0]).filter(t => t && t.trim().length > 0).slice(0, 500); 
          bulkData = texts;
          document.getElementById('drop-zone-text').innerHTML = `<b>${file.name}</b> loaded<br>${texts.length} reviews found (max 500).`;
        },
        header: true
      });
    }

    // Bulk Analyze
    const btnBulk = document.getElementById('btn-bulk');
    if (btnBulk) {
      const newBtnBulk = btnBulk.cloneNode(true);
      if(btnBulk.parentNode) {
        btnBulk.parentNode.replaceChild(newBtnBulk, btnBulk);
        newBtnBulk.addEventListener('click', async () => {
          let texts = [];
          const methodInput = document.querySelector('input[name="bulk-method"]:checked');
          if(!methodInput) return;
          const method = methodInput.value;
          if (method === 'text') {
            const txtArea = document.getElementById('bulk-text');
            if(txtArea) texts = txtArea.value.split('\n').filter(t => t.trim().length > 0);
          } else {
            texts = bulkData;
          }

          if (texts.length === 0) {
            alert("No reviews to analyze."); return;
          }

          const activeModelBtn = document.querySelector('#bulk-model-select .btn.active');
          const modelName = activeModelBtn ? activeModelBtn.getAttribute('data-model') : 'lr';

          newBtnBulk.disabled = true;
          newBtnBulk.innerHTML = '<i data-lucide="loader" class="spin"></i> Processing...';
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
              
              window.bulkExportData = data.results; 

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
            newBtnBulk.disabled = false;
            newBtnBulk.innerHTML = 'Analyze';
          }
        });
      }
    }
    
    // Bulk Export
    const exportCsv = document.getElementById('export-csv');
    if (exportCsv) {
      const newExport = exportCsv.cloneNode(true);
      if(exportCsv.parentNode) {
        exportCsv.parentNode.replaceChild(newExport, exportCsv);
        newExport.addEventListener('click', (e) => {
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
    }
  }

  // ============================================
  // INITIALIZATION
  // ============================================
  initRouter();
  initPageEvents();
});
