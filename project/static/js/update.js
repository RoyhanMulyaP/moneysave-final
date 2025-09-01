const doneBtn = document.getElementById("doneBtn");
  const userId = document.getElementById("userId").value;

  doneBtn.addEventListener("click", async () => {
    const userData = {
      nik: document.getElementById("nik").value,
      nama: document.getElementById("nama").value,
      tgl_lahir: document.getElementById("ttl").value,
      agama: document.getElementById("agama").value,
      alamat: document.getElementById("alamat").value,
      jenis_kelamin: document.getElementById("jenis_kelamin").value,
      email: document.getElementById("email").value,
      hp: document.getElementById("hp").value,
      no_rek: document.getElementById("rekening").value,
      nama_rekening: document.getElementById("username").value,
      cabang: document.getElementById("cabang").value,
      tgl_rekening: document.getElementById("tgl_rekening").value
    };

    const formData = new FormData();
    formData.append("userId", userId);
    for (const key in userData) {
      formData.append(key, userData[key]);
    }

    const response = await fetch("/update_data_lengkap", {
      method: "POST",
      body: formData
    });

    const result = await response.json();

    if (result.success) {
      window.location.href = "/sign_up";
    } else {
      alert("Terjadi kesalahan: " + result.error);
    }
  });