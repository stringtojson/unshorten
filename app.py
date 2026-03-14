import streamlit as st
import requests
import re

# Konfigurasi Tampilan Web
st.set_page_config(page_title="Marketplace Link Cleaner", page_icon="🛒")

st.title("🛒 Marketplace Unshortener & Cleaner")
st.markdown("Masukkan link **Tokopedia (vt)** atau **Shopee (s.shopee)** di bawah.")

# Input area
input_text = st.text_area("List URL Pendek (Satu per baris):", height=200, placeholder="https://vt.tokopedia.com/...\nhttps://s.shopee.co.id/...")

def clean_marketplace_url(url_pendek):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    try:
        # Proses Unshorten (Mengikuti redirect sampai mentok)
        res = requests.get(url_pendek, headers=headers, allow_redirects=True, timeout=15)
        url_panjang = res.url
        
        # --- LOGIKA TOKOPEDIA ---
        if "tokopedia.com" in url_panjang:
            match = re.search(r'(?:product|pdp)/(\d+)', url_panjang) or re.search(r'/(\d{15,})', url_panjang)
            if match:
                return f"https://shop-id.tokopedia.com/pdp/{match.group(1)}"
            return f"Tokopedia (ID Tak Temu): {url_panjang[:60]}..."

        # --- LOGIKA SHOPEE ---
        elif "shopee.co.id" in url_panjang:
            # Cari pola product/SHOPID/ITEMID
            match_shopee = re.search(r'product/(\d+)/(\d+)', url_panjang)
            if match_shopee:
                shop_id = match_shopee.group(1)
                item_id = match_shopee.group(2)
                return f"https://shopee.co.id/product/{shop_id}/{item_id}"
            
            # Fallback jika URL Shopee tipe lain tapi punya ID unik di akhir
            match_alt = re.search(r'i\.(\d+)\.(\d+)', url_panjang)
            if match_alt:
                return f"https://shopee.co.id/product/{match_alt.group(1)}/{match_alt.group(2)}"
            
            return f"Shopee (ID Tak Temu): {url_panjang[:60]}..."

        return f"Bukan Tokped/Shopee: {url_panjang[:60]}..."

    except Exception as e:
        return f"Error: {str(e)}"

if st.button("Bersihkan Semua Link"):
    urls = [u.strip() for u in input_text.split('\n') if u.strip()]
    
    if not urls:
        st.warning("Paste link-nya dulu, Bro!")
    else:
        hasil_list = []
        progress_text = st.empty()
        progress_bar = st.progress(0)
        
        for i, url in enumerate(urls):
            progress_text.text(f"Memproses {i+1} dari {len(urls)} link...")
            hasil = clean_marketplace_url(url)
            hasil_list.append(hasil)
            progress_bar.progress((i + 1) / len(urls))
        
        progress_text.text("✅ Semua link selesai diproses!")
        
        # Tampilkan Hasil
        st.success(f"Berhasil merapikan {len(hasil_list)} link!")
        st.text_area("Hasil Bersih:", value="\n".join(hasil_list), height=250)
        
        # Tombol Download
        st.download_button(
            label="📥 Download Hasil (.txt)",
            data="\n".join(hasil_list),
            file_name="hasil_bersih_marketplace.txt",
            mime="text/plain"
        )
