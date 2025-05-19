

let sikayetHaritasi;
let sikayetIsareti;

function haritayiBaslat(){


 console.log("Google Maps Haritası Başlatılıyor..."); // ✅ DEBUG MESAJI
    let mapElement = document.getElementById("complaint-map");

    if (!mapElement) {
        console.error(" Hata: complaint-map div'i bulunamadı!");
        return;
    }

    sikayetHaritasi = new google.maps.Map(mapElement, {
        center: { lat: 41.4514, lng: 31.7931 }, // Varsayılan merkez: Zonguldak
        zoom: 12
    });

    sikayetIsareti = new google.maps.Marker({
        position: { lat: 41.4514, lng: 31.7931 }, // Varsayılan nokta
        map: sikayetHaritasi,
        title: "Şikayet Konumu"
    });

    console.log("✅ Harita başarıyla yüklendi!");




}

function showComplaintDetails(id) {
    console.log(`Şikayet Detayları Yükleniyor: ${id}`); // DEBUG
    aktifSikayetID = id

    fetch(`/get_complaint_details/${id}`)
        .then(response => response.json())
        .then(complaint => {
            console.log("Gelen Şikayet Verisi:", complaint); // DEBUG

            if (complaint.error) {
                document.getElementById("complaint-detail").innerHTML = "<h2>Şikayet bulunamadı</h2>";
            } else {



                document.getElementById("complaint-detail").innerHTML = `
                    <h2>Şikayet Detayları</h2>
                    <p><strong>Konu:</strong> ${complaint.sikayetKonu}</p>
                    <p><strong>Açıklama:</strong> ${complaint.sikayetAciklama}</p>
                    <p><strong>Tarih:</strong> ${new Date(complaint.sikayetTarih).toLocaleDateString('tr-TR')} /*${complaint.sikayetTarih}*/</p>
                    <img src="${complaint.sikayetResim}" alt="Şikayet Resmi" class="complaint-image">
                    <p><strong>Durum:</strong> ${
                        complaint.durum == 1 ? "Aktif Şikayet" :
                        complaint.durum == 2 ? "Çözüldü" :
                        complaint.durum == 3 ? "Çözülemedi" :
                        "Bilinmiyor"
                    }</p>



                    <div class="button-group">
                    <button class="btn btn-success" onclick="sikayetDurumGuncelle(2)">Şikayet Çözüldü</button>
                    <button class="btn btn-danger" onclick="sikayetDurumGuncelle(3)">Şikayet Çözülemedi</button>
                    </div>


                    <!--
                    <div id="complaint-map" style = "height: 300px; width: 300px; border: 1px solid black;">

                    </div>
                    -->
                    <div class="konum-container">
                    <h3>Konum</h3>
                    <div id="complaint-map"></div>
                    </div>
                `;

                // eğer enlem ve boylam varsa haritayı güncelle
                if (complaint.sikayetEnlem && complaint.sikayetBoylam){
                    let sikayetKonumu = {
                        lat: parseFloat(complaint.sikayetEnlem),
                        lng: parseFloat(complaint.sikayetBoylam)
                    };
                    console.log(`Şikayet Konumu Güncelleniyor: ${sikayetKonumu.lat}, ${sikayetKonumu.lng}`); // ✅ DEBUG                    //sikayetHaritasi.setCenter(sikayetKonumu);

                    sikayetHaritasi = new google.maps.Map(document.getElementById("complaint-map"), {
                    center: sikayetKonumu,
                    zoom: 15
                    });

                    sikayetIsareti = new google.maps.Marker({
                    position: sikayetKonumu,
                    map: sikayetHaritasi,
                    title: "Şikayet Konumu"
                    });

                }
                else{
                    console.log("Bu şikayet için konum bilgisi yok!");
                }
            }
        })
        .catch(error => console.error("Hata:", error));
}

function sikayetDurumGuncelle(yeniDurum){

    if (!aktifSikayetID){
        alert("Şikayet id bulunamadı");
        return;
    }

    fetch(`/sikayet_durum_guncelle/${aktifSikayetID}/${yeniDurum}`,{method: 'POST'}).then(res => {

        if (res.ok) {
            alert("Şikayet durumu güncellendi!");
        } else {
            alert("Güncelleme başarısız oldu.");
        }

    });

}

document.addEventListener("DOMContentLoaded", () => {
    haritayiBaslat();
});

