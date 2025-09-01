const modalOverlay = document.getElementById("modalOverlay");
const openModalBtn = document.getElementById("openModalBtn");
const closeModalBtn = document.getElementById("closeModalBtn");
const closeModalBtn2 = document.getElementById("closeModalBtn2");
const btnTambahRincian = document.querySelector(".btn-tambah-rincian");
const rincianContainer = document.getElementById("rincianContainer");
const defaultRincianHTML = rincianContainer.innerHTML;
const btnSimpanTarget = document.getElementById("btnSimpanTarget");

openModalBtn.addEventListener("click", () => {
  modalOverlay.style.display = "flex";
});

[closeModalBtn, closeModalBtn2].forEach((btn) => {
  btn.addEventListener("click", () => {
    modalOverlay.style.display = "none";
    rincianContainer.innerHTML = defaultRincianHTML;
    attachTambahListener();
  });
});

modalOverlay.addEventListener("click", (e) => {
  if (e.target === modalOverlay) {
    modalOverlay.style.display = "none";
    rincianContainer.innerHTML = defaultRincianHTML;
    attachTambahListener();
  }
});

function attachTambahListener() {
  const btnTambah = rincianContainer.querySelector(".btn-tambah-rincian");
  btnTambah.addEventListener("click", (e) => {
    e.preventDefault();

    const newItem = document.createElement("div");
    newItem.classList.add("rincian-item");

    const inputNama = document.createElement("input");
    inputNama.type = "text";
    inputNama.placeholder = "Pengeluaran";

    const inputJumlah = document.createElement("input");
    inputJumlah.type = "text";
    inputJumlah.value = "Rp 0";

    newItem.appendChild(inputNama);
    newItem.appendChild(inputJumlah);

    rincianContainer.insertBefore(newItem, btnTambah);
  });
}

btnSimpanTarget.addEventListener("click", () => {
  const namaTarget = document.getElementById("namaTarget").value;
  const tenggatTarget = document.getElementById("tenggatTarget").value;

  const rincianContainer = document.getElementById("rincianContainer");
  const rincianItems = rincianContainer.querySelectorAll(".rincian-item");

  let rincianData = [];
  rincianItems.forEach(item => {
    const pengeluaran = item.querySelector('input[type="text"]').value;
    const uang = item.querySelectorAll('input[type="text"]')[1].value.replace(/[Rp\s,.]/g,''); // bersihkan Rp
    if(pengeluaran) {
      rincianData.push({ pengeluaran, uang });
    }
  });

  fetch("/simpan_target", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      namaTarget,
      tenggatTarget,
      rincian: rincianData
    })
  })
  .then(res => res.json())
  .then(data => {
    if(data.success){
      alert("Target berhasil disimpan!");
      // tutup modal dan reset input
      document.getElementById("modalOverlay").style.display = "none";
      document.getElementById("rincianContainer").innerHTML = `
        <div class="rincian-item">
          <input type="text" placeholder="Pengeluaran" />
          <input type="text" value="Rp 0" />
        </div>
        <div class="rincian-item">
          <input type="text" placeholder="Pengeluaran" />
          <input type="text" value="Rp 0" />
        </div>
        <button class="btn-tambah-rincian">
          <span class="plus-icon">+</span> Tambah Rincian Pengeluaran
        </button>
      `;
    } else {
      alert("Terjadi kesalahan: " + data.error);
    }
  });
});

attachTambahListener();
