# ai_model/model.py
import numpy as np
from google import genai
from google.genai import types
import dotenv
import os
import markdown
dotenv.load_dotenv()

def analyze_image(image):
    client = genai.Client(api_key=os.getenv("api_key"))
    response = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        "ini merupakan aplikasi ai radiologi untuk simrs khanza. Anda adalah asisten AI radiologi. Analisis gambar radiologi ini secara menyeluruh dan berikan ringkasan diagnostik dengan struktur berikut:\n\n"
        "1. **Temuan**: Jelaskan kelainan atau abnormalitas yang terlihat pada gambar. Sebutkan secara spesifik bentuk, kepadatan, atau tanda-tanda tidak normal.\n"
        "2. **Area Anatomi**: Sebutkan bagian tubuh mana yang terdampak.\n"
        "3. **Kemungkinan Diagnosis**: Berikan dugaan kondisi medis berdasarkan hasil gambar. Jelaskan secara singkat dalam bahasa awam agar mudah dimengerti.\n"
        "4. **Tingkat Keparahan**: Jika ada kelainan, nilai tingkat keparahannya (ringan, sedang, berat) serta urgensinya.\n"
        "5. **Rekomendasi**: Sarankan tindak lanjut seperti pemeriksaan lanjutan, rujukan, atau tindakan medis lainnya jika diperlukan.\n\n"
        "Gunakan bahasa yang ringkas, akurat secara medis, dan sertakan penjelasan dalam istilah awam bila perlu. jika gambar bukan gambar medis, maka berikan penjelasan bahwa gambar tersebut bukan gambar medis dan berikan peringatan jangan mengguanakan sumber daya ini untuk bermain main dengan data tidak benar.",
        image])
    response2 = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        f"Berdasarkan ringkasan diagnostik berikut:\n\n{response.text}\n\n"
        "Berikan daftar kemungkinan kode ICD-10 yang relevan. Sertakan kode, deskripsi medis, dan penjelasan singkat mengapa kode tersebut cocok dengan temuan yang ada dan buat dalam bentuk tabel. jika bukan gambar medis maka hanya perlu respon \"-\""])
    response3 = client.models.generate_content(
    model="gemini-2.0-flash",
    contents=[
        f"{response.text}\n\n{response2.text}\n\n"
        "Berdasarkan analisis dan kode ICD di atas, berikan daftar kemungkinan pengobatan atau penanganan. Untuk setiap kondisi, sertakan pengobatan standar, rekomendasi gaya hidup (jika ada), dan rencana tindak lanjut. Susun secara jelas dan utamakan keselamatan pasien. jika bukan gambar medis maka hanya perlu respon \"-\""])
    findings = {
        'Hasil Analisis': markdown.markdown(response.text, extensions=['tables']),
        'Kemungkinan kode ICD': markdown.markdown(response2.text, extensions=['tables']),
        'Kemungkinan Penanganan': markdown.markdown(response3.text, extensions=['tables'])
    }
    
    return findings
