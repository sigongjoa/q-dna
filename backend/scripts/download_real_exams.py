import os
import requests
import urllib.parse

# Setup Directories
DATA_DIR = os.path.join("data", "raw", "exams")
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# --- 1. KJMO Links (Direct) ---
KJMO_LINKS = [
    # 2025
    ("KJMO_2025_TypeA_Prob.pdf", "https://www.kms.or.kr/inc/attach_download.php?r_name=3068357271_abcdbe72_2025KJMO_EAB080.pdf&f_name=2025KJMO_%EA%B0%80.pdf"),
    ("KJMO_2025_TypeB_Prob.pdf", "https://www.kms.or.kr/inc/attach_download.php?r_name=3068357271_5df6abdf_2025KJMO_EB8298.pdf&f_name=2025KJMO_%EB%82%98.pdf"),
    # 2024
    ("KJMO_2024_TypeA_Prob.pdf", "https://www.kms.or.kr/inc/attach_download.php?r_name=3068357271_a6604fc0_2024KJMOEAB080.pdf&f_name=2024KJMO%EA%B0%80.pdf"),
    ("KJMO_2024_TypeB_Prob.pdf", "https://www.kms.or.kr/inc/attach_download.php?r_name=3068357271_d3931cf8_2024KJMOEB8298.pdf&f_name=2024KJMO%EB%82%98.pdf"),
    # 2023
    ("KJMO_2023_TypeA_Prob.pdf", "https://www.kms.or.kr/inc/attach_download.php?r_name=3068357271_ad47e310_2023KJMO28EAB080ED989529.pdf&f_name=2023KJMO%28%EA%B0%80%ED%98%95%29.pdf"),
    ("KJMO_2023_TypeB_Prob.pdf", "https://www.kms.or.kr/inc/attach_download.php?r_name=3068357271_f81e433b_2023KJMO28EB8298ED989529.pdf&f_name=2023KJMO%28%EB%82%98%ED%98%95%29.pdf"),
    # 2022
    ("KJMO_2022_TypeA_Prob.pdf", "https://www.kms.or.kr/inc/attach_download.php?r_name=3068357271_8f1f66a2_2022kjmoEAB080.pdf&f_name=2022kjmo%EA%B0%80.pdf"),
    ("KJMO_2022_TypeB_Prob.pdf", "https://www.kms.or.kr/inc/attach_download.php?r_name=3068357271_0551c190_2022kjmoEB8298.pdf&f_name=2022kjmo%EB%82%98.pdf"),
]

# --- 2. KMA Links (Constructed) ---
# Base: https://admin.kma-e.com/common/filedownload.aspx?filepath=/upload/testsheet/&filename=...
KMA_BASE_URL = "https://admin.kma-e.com/common/filedownload.aspx?filepath=/upload/testsheet/&filename="

# Pattern found: kma_sheet_11_1_prob.pdf (2025 1st half, grade 1) -> 11 seems to be the exam code
# Let's try to download Grade 3-6 (Simhwa Target) for Exam Code 11 (2025 1st)
KMA_TARGETS = []
for grade in range(3, 7):
    # Prob
    filename_prob = f"kma_sheet_11_{grade}_prob.pdf"
    KMA_TARGETS.append((f"KMA_2025_1H_G{grade}_Prob.pdf", filename_prob))
    # Answer (Dab)
    filename_dab = f"kma_sheet_11_{grade}_dab.pdf"
    KMA_TARGETS.append((f"KMA_2025_1H_G{grade}_Ans.pdf", filename_dab))

def download_file(url, filename):
    print(f"[*] Downloading {filename}...")
    try:
        # User-Agent headers are important for some WAFs
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            file_path = os.path.join(DATA_DIR, filename)
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            print(f"[+] Saved to {file_path}")
        else:
            print(f"[-] Failed: Status {response.status_code} for {url}")
    except Exception as e:
        print(f"[!] Error downloading {filename}: {e}")

def main():
    print("=== Starting Real Exam Data Download ===")
    
    # KJMO
    print("\n--- Downloading KJMO Papers ---")
    for filename, url in KJMO_LINKS:
        download_file(url, filename)
        
    # KMA
    print("\n--- Downloading KMA Papers (Pattern Based) ---")
    for save_name, remote_name in KMA_TARGETS:
        # Need to encode filename in URL properly if it has spaces/Korean, but these are English
        full_url = KMA_BASE_URL + remote_name
        download_file(full_url, save_name)

    print("\n=== All Tasks Completed ===")

if __name__ == "__main__":
    main()
