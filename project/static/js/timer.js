const countdownElem = document.getElementById('countdown');
let sisaWaktu = parseInt(countdownElem.getAttribute('data-time'), 10);

function updateTimer() {
  if (sisaWaktu <= 0) {
    countdownElem.textContent = "Waktu Habis!";
    clearInterval(timerInterval);
    return;
  }
  
  let jam = Math.floor(sisaWaktu / 3600);
  let menit = Math.floor((sisaWaktu % 3600) / 60);
  let detik = sisaWaktu % 60;

  countdownElem.textContent =
    `${String(jam).padStart(2,'0')}:${String(menit).padStart(2,'0')}:${String(detik).padStart(2,'0')}`;
  sisaWaktu--;
}

updateTimer();
const timerInterval = setInterval(updateTimer, 1000);
