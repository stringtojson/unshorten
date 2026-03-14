import streamlit as st
import requests
import re
import time

# Konfigurasi Halaman
st.set_page_config(page_title="Universal Link Cleaner", page_icon="🔗")

st.title("🔗 Marketplace Link Cleaner")
st.markdown("Masukkan link pendek **Tokopedia** atau **Shopee** untuk mendapatkan URL bersihnya.")

# Input Area
input_text = st.text_area("List Link Pendek (Satu per baris):", height=200, placeholder="https://vt.tokopedia.com/...\nhttps://s.shopee.co.id/...")

def clean_marketplace_url(url_pendek, session):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'id-ID,id;q=0.9'
    }
    try:
        # Proses Unshorten dengan Session
        res = session.get(url_pendek, headers=headers, allow_redirects=True, timeout=20)
        url_panjang = res.url
        
        # --- LOGIKA TOKOPEDIA ---
        if "tokopedia.com" in url_panjang:
            match = re.search(r'(?:product|pdp)/(\d+)', url_panjang) or re.search(r'/(\d{15,})', url_panjang)
            if match:
                return f"https://shop-id.tokopedia.com/pdp/{match.group(1)}"

        # --- LOGIKA SHOPEE (Multi-pola) ---
        elif "shopee.co.id" in url_panjang:
            # Pola 1: product/SHOPID/ITEMID
            match_p1 = re.search(r'product/(\d+)/(\d+)', url_panjang)
            if match_p1:
                return f"https://shopee.co.id/product/{match_p1.group(1)}/{match_p1.group(2)}"
            
            # Pola 2: /username/SHOPID/ITEMID (kasus redirect menengah)
            match_p2 = re.search(r'shopee\.co\.id\/[\w.-]+\/(\d+)\/(\d+)', url_panjang)
            if match_p2:
                return f"https://shopee.co.id/product/{match_p2.group(1)}/{match_p2.group(2)}"

            # Pola 3: Parameter itemid & shopid
            item_id = re.search(r'itemid=(\d+)', url_panjang)
            shop_id = re.search(r'shopid=(\d+)', url_panjang)
            if item_id and shop_id:
                return f"https://shopee.co.id/product/{shop_id.group(1)}/{item_id.group(1)}"

        return url_panjang # Jika gagal ekstrak, kembalikan URL panjang apa adanya
        
    except:
        return None

if st.button("Proses & Bersihkan"):
    urls = [u.strip() for u in input_text.split('\n') if u.strip()]
    
    if not urls:
        st.warning("Masukkan link dulu!")
    else:
        hasil_list = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        # Inisialisasi Session
        session = requests.Session()
        
        for i, url in enumerate(urls):
            status_text.text(f"Memproses {i+1}/{len(urls)}...")
            hasil = clean_marketplace_url(url, session)
            
            if hasil:
                # Logika Hapus Duplikat
                if hasil not in hasil_list:
                    hasil_list.append(hasil)
            
            progress_bar.progress((i + 1) / len(urls))
            # Jeda dikit biar aman dari ban
            time.sleep(0.5)
        
        status_text.text("✅ Selesai!")
        
        if hasil_list:
            st.success(f"Ditemukan {len(hasil_list)} link unik.")
            
            # Output Box (Hanya Link Saja)
            hasil_akhir_teks = "\n".join(hasil_list)
            st.text_area("Hasil URL Bersih:", value=hasil_akhir_teks, height=300)
            
            # Download Button
            st.download_button(
                label="📥 Simpan sebagai .txt",
                data=hasil_akhir_teks,
                file_name="hasil_bersih.txt",
                mime="text/plain"
            )
        else:
            st.error("Gagal memproses link. Pastikan link valid.")
