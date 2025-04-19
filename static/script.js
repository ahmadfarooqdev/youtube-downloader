const form = document.getElementById('downloadForm');
const percent = document.getElementById('percent');
const bar = document.getElementById('bar');
const result = document.getElementById('result');
const progressWrapper = document.getElementById('progressWrapper');

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  percent.textContent = '0%';
  bar.style.width = '0%';
  progressWrapper.style.display = 'block';
  result.innerHTML = '';

  const formData = new FormData(form);
  const response = await fetch('/download', {
    method: 'POST',
    body: formData
  });

  const data = await response.json();
  const id = data.download_id;

  const check = setInterval(async () => {
    const res = await fetch(`/progress/${id}`);
    const json = await res.json();

    if (json.progress) {
      percent.textContent = json.progress;
      const clean = parseFloat(json.progress.replace('%', '')) || 0;
      bar.style.width = `${clean}%`;
    }

    if (json.status === 'done') {
      clearInterval(check);
      result.innerHTML = `<a href="/get-file/${id}" class="download-link">⬇ Click to Download</a>`;
    }

    if (json.status === 'error') {
      clearInterval(check);
      result.innerHTML = `<p style="color:red;">❌ Error: ${json.error}</p>`;
    }
  }, 2000);

 
});
