import streamlit as st
import requests
import re
import pandas as pd

# Konfigurasi Tampilan Web
st.set_page_config(page_title="Tokopedia Link Cleaner", page_icon="🛍️")

st.title("🛍️ Tokopedia Unshortener & Cleaner")
st.markdown("Masukkan link **vt.tokopedia.com** di bawah untuk merapikan formatnya.")

# Input area
input_text = st.text_area("List URL Pendek (Satu per baris):", height=200, placeholder="https://vt.tokopedia.com/t/ZS...")

def clean_tokped_url(url_pendek):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'}
    try:
        # Proses Unshorten (Server-side Python, NO CORS!)
        res = requests.get(url_pendek, headers=headers, allow_redirects=True, timeout=10)
        url_panjang = res.url
        
        # Ambil ID Produk
        match = re.search(r'(?:product|pdp)/(\d+)', url_panjang) or re.search(r'/(\d{15,})', url_panjang)
        if match:
            return f"https://shop-id.tokopedia.com/pdp/{match.group(1)}"
        return f"Gagal Ekstrak ID: {url_panjang[:50]}..."
    except Exception as e:
        return f"Error: {str(e)}"

if st.button("Proses Sekarang"):
    urls = [u.strip() for u in input_text.split('\n') if u.strip()]
    
    if not urls:
        st.warning("Masukkan link dulu, Bro!")
    else:
        hasil_list = []
        progress_bar = st.progress(0)
        
        for i, url in enumerate(urls):
            hasil = clean_tokped_url(url)
            hasil_list.append(hasil)
            # Update progress
            progress_bar.progress((i + 1) / len(urls))
        
        # Tampilkan Hasil
        st.success(f"Berhasil memproses {len(hasil_list)} link!")
        st.text_area("Hasil Rapi:", value="\n".join(hasil_list), height=200)
        
        # Tombol Download
        st.download_button(
            label="Simpan ke .TXT",
            data="\n".join(hasil_list),
            file_name="hasil_bersih_tokped.txt",
            mime="text/plain"
        )