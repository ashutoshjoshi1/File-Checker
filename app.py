from flask import Flask, request, render_template
import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime
import bz2  # Used for L0 files

app = Flask(__name__)
server = app.server
app.secret_key = "your_secret_key"  # Replace with a secure key

# Mapping of sites (ignoring URL values if any)
sites = [
    {"location": "Agam", "number": "211"},
    {"location": "AldineTX", "number": "61"},
    {"location": "AliceSprings", "number": "129"},
    {"location": "Altzomoni", "number": "65"},
    {"location": "ArlingtonTX", "number": "207"},
    {"location": "Athens-NOA", "number": "119"},
    {"location": "AtlantaGA-Conyers", "number": "158"},
    {"location": "AtlantaGA-GATech", "number": "173"},
    {"location": "AtlantaGA-SouthDeKalb", "number": "237"},
    {"location": "AtlantaGA", "number": "158"},
    {"location": "AustinTX", "number": "257"},
    {"location": "Bandung", "number": "210"},
    {"location": "Bangkok", "number": "190"},
    {"location": "Banting", "number": "78"},
    {"location": "BayonneNJ", "number": "38"},
    {"location": "Beijing-RADI", "number": "171"},
    {"location": "BeltsvilleMD", "number": "80"},
    {"location": "Berlin", "number": "132"},
    {"location": "BlueHillMA", "number": "139"},
    {"location": "BostonMA", "number": "155"},
    {"location": "BoulderCO-NCAR", "number": "204"},
    {"location": "BoulderCO", "number": "57"},
    {"location": "Bremen", "number": "21"},
    {"location": "BristolPA", "number": "134"},
    {"location": "BronxNY", "number": "147"},
    {"location": "Brussels-Uccle", "number": "162"},
    {"location": "Bucharest", "number": "111"},
    {"location": "BuenosAires", "number": "114"},
    {"location": "BuffaloNY", "number": "206"},
    {"location": "Busan", "number": "20"},
    {"location": "Cabauw", "number": "118"},
    {"location": "Calakmul", "number": "141"},
    {"location": "CambridgeBay", "number": "281"},
    {"location": "CambridgeMA", "number": "26"},
    {"location": "CameronLA", "number": "260"},
    {"location": "CapeElizabethME", "number": "184"},
    {"location": "Cebu", "number": "225"},
    {"location": "ChapelHillNC", "number": "166"},
    {"location": "CharlesCityVA", "number": "31"},
    {"location": "ChelseaMA", "number": "153"},
    {"location": "ChiangMai", "number": "213"},
    {"location": "ChicagoIL", "number": "249"},
    {"location": "Cologne", "number": "67"},
    {"location": "ComodoroRivadavia", "number": "124"},
    {"location": "Cordoba", "number": "113"},
    {"location": "CornwallCT", "number": "179"},
    {"location": "CorpusChristiTX", "number": "258"},
    {"location": "Daegu", "number": "229"},
    {"location": "Dalanzadgad", "number": "217"},
    {"location": "Davos", "number": "120"},
    {"location": "DearbornMI", "number": "39"},
    {"location": "DeBilt", "number": "82"},
    {"location": "Dhaka", "number": "76"},
    {"location": "Downsview", "number": "103"},
    {"location": "EastProvidenceRI", "number": "185"},
    {"location": "EdwardsCA", "number": "74"},
    {"location": "Egbert", "number": "108"},
    {"location": "EssexMD", "number": "75"},
    {"location": "Eureka-0PAL", "number": "280"},
    {"location": "Eureka-PEARL", "number": "144"},
    {"location": "FairbanksAK", "number": "174"},
    {"location": "Fajardo", "number": "60"},
    {"location": "FortMcKay", "number": "122"},
    {"location": "FortYatesND", "number": "205"},
    {"location": "Fukuoka", "number": "199"},
    {"location": "Gongju-KNU", "number": "230"},
    {"location": "Granada", "number": "238"},
    {"location": "GrandForksND", "number": "200"},
    {"location": "GreenbeltMD", "number": "2"},
    {"location": "Haldwani-ARIES", "number": "250"},
    {"location": "HamptonVA-HU", "number": "156"},
    {"location": "HamptonVA", "number": "37"},
    {"location": "Heidelberg", "number": "133"},
    {"location": "Helsinki", "number": "105"},
    {"location": "HoustonTX-SanJacinto", "number": "261"},
    {"location": "HoustonTX", "number": "25"},
    {"location": "HuntsvilleAL", "number": "66"},
    {"location": "Ilocos", "number": "219"},
    {"location": "Incheon-ESC", "number": "189"},
    {"location": "Innsbruck", "number": "106"},
    {"location": "IowaCityIA-WHS", "number": "246"},
    {"location": "Islamabad-NUST", "number": "73"},
    {"location": "Izana", "number": "101"},
    {"location": "Jeonju", "number": "241"},
    {"location": "Juelich", "number": "30"},
    {"location": "KenoshaWI", "number": "167"},
    {"location": "Kobe", "number": "198"},
    {"location": "Kosetice", "number": "239"},
    {"location": "LaPaz", "number": "283"},
    {"location": "LaPorteTX", "number": "11"},
    {"location": "LapwaiID", "number": "188"},
    {"location": "LibertyTX", "number": "143"},
    {"location": "Lindenberg", "number": "130"},
    {"location": "LondonderryNH", "number": "183"},
    {"location": "LynnMA", "number": "107"},
    {"location": "MadisonCT", "number": "186"},
    {"location": "ManhattanKS", "number": "165"},
    {"location": "ManhattanNY-CCNY", "number": "135"},
    {"location": "MaunaLoaHI", "number": "56"},
    {"location": "MexicoCity-UNAM", "number": "142"},
    {"location": "MexicoCity-Vallejo", "number": "157"},
    {"location": "MiamiFL-FIU", "number": "256"},
    {"location": "MountainViewCA", "number": "34"},
    {"location": "Nagoya", "number": "197"},
    {"location": "Nainital-ARIES", "number": "251"},
    {"location": "NewBrunswickNJ", "number": "69"},
    {"location": "NewHavenCT", "number": "64"},
    {"location": "NewLondonCT", "number": "236"},
    {"location": "NewOrleansLA-XULA", "number": "85"},
    {"location": "NyAlesund", "number": "152"},
    {"location": "OldFieldNY", "number": "51"},
    {"location": "Palau", "number": "131"},
    {"location": "Palawan", "number": "221"},
    {"location": "PhiladelphiaPA", "number": "166"},
    {"location": "PhnomPenh", "number": "215"},
    {"location": "PittsburghPA", "number": "187"},
    {"location": "Pontianak", "number": "212"},
    {"location": "Potchefstroom-METSI", "number": "53"},
    {"location": "QueensNY", "number": "55"},
    {"location": "QuezonCity", "number": "224"},
    {"location": "RichmondCA", "number": "52"},
    {"location": "Rome-IIA", "number": "138"},
    {"location": "Rome-ISAC", "number": "115"},
    {"location": "Rome-SAP", "number": "117"},
    {"location": "Rotterdam-Haven", "number": "84"},
    {"location": "SaltLakeCityUT-Hawthorne", "number": "72"},
    {"location": "SaltLakeCityUT", "number": "154"},
    {"location": "SanJoseCA", "number": "181"},
    {"location": "Sapporo", "number": "195"},
    {"location": "Seosan", "number": "164"},
    {"location": "Seoul-KU", "number": "235"},
    {"location": "Seoul-SNU", "number": "149"},
    {"location": "Seoul", "number": "27"},
    {"location": "Singapore-NUS", "number": "77"},
    {"location": "Songkhla", "number": "214"},
    {"location": "SouthJordanUT", "number": "139"},
    {"location": "StGeorge", "number": "109"},
    {"location": "StonyPlain", "number": "123"},
    {"location": "Suwon-USW", "number": "231"},
    {"location": "SWDetroitMI", "number": "147"},
    {"location": "Tel-Aviv", "number": "182"},
    {"location": "Thessaloniki", "number": "240"},
    {"location": "Tokyo-Sophia", "number": "192"},
    {"location": "Tokyo-TMU", "number": "194"},
    {"location": "Toronto-CNTower", "number": "243"},
    {"location": "Toronto-Scarborough", "number": "145"},
    {"location": "Toronto-West", "number": "108"},
    {"location": "Trollhaugen", "number": "242"},
    {"location": "Tsukuba-NIES-West", "number": "163"},
    {"location": "Tsukuba-NIES", "number": "176"},
    {"location": "Tsukuba", "number": "193"},
    {"location": "TubaCityAZ", "number": "254"},
    {"location": "TucsonAZ", "number": "253"},
    {"location": "TurlockCA", "number": "248"},
    {"location": "TylerTX", "number": "259"},
    {"location": "Ulaanbaatar", "number": "216"},
    {"location": "Ulsan", "number": "150"},
    {"location": "Vientiane", "number": "218"},
    {"location": "VirginiaBeachVA-CBBT", "number": "255"},
    {"location": "WacoTX", "number": "207"},
    {"location": "Wakkerstroom", "number": "159"},
    {"location": "WallopsIslandVA", "number": "40"},
    {"location": "Warsaw-UW", "number": "270"},
    {"location": "WashingtonDC", "number": "140"},
    {"location": "WestportCT", "number": "177"},
    {"location": "WhittierCA", "number": "247"},
    {"location": "Windsor-West", "number": "208"},
    {"location": "WrightwoodCA", "number": "68"},
    {"location": "Yokosuka", "number": "146"},
    {"location": "Yongin", "number": "232"}
]

def get_most_recent_file_L0(location, pandora_number):
    """
    For the L0 directory:
      - Build the URL: https://data.ovh.pandonia-global-network.org/<location>/Pandora<pandora_number>s1/L0/
      - Look for files matching:
        Pandora<pandora_number>s1_<location>_<YYYYMMDD>_L0.txt.bz2
      - Return the most recent file's name and the extracted date (formatted as YYYY-MM-DD).
    """
    base_url = f"https://data.ovh.pandonia-global-network.org/{location}/Pandora{pandora_number}s1/L0/"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching L0 URL: {e}", base_url, None, None

    soup = BeautifulSoup(response.text, 'html.parser')
    pattern = re.compile(rf"Pandora{pandora_number}s1_{location}_(\d{{8}})_L0\.txt\.bz2")
    files = []
    for link in soup.find_all('a'):
        file_candidate = link.get('href') or link.get_text()
        if file_candidate:
            match = pattern.search(file_candidate)
            if match:
                date_str = match.group(1)
                try:
                    date_obj = datetime.strptime(date_str, '%Y%m%d')
                    files.append((date_obj, file_candidate))
                except ValueError:
                    continue
    if files:
        files.sort(key=lambda x: x[0], reverse=True)
        latest_date, latest_file = files[0]
        formatted_date = latest_date.strftime('%Y-%m-%d')
        return None, base_url, latest_file, formatted_date
    else:
        return None, base_url, None, None

def get_l2_file_last_line_dates(location, pandora_number):

    base_url = f"https://data.ovh.pandonia-global-network.org/{location}/Pandora{pandora_number}s1/L2/"
    try:
        response = requests.get(base_url)
        response.raise_for_status()
    except Exception as e:
        return f"Error fetching L2 URL: {e}", base_url, []

    soup = BeautifulSoup(response.text, 'html.parser')
    # Updated regex pattern to match new L2 filename format
    pattern = re.compile(rf"Pandora{pandora_number}s1_{location}_L2_[a-z0-9-]+\.txt", re.IGNORECASE)
    files = []
    for link in soup.find_all('a'):
        file_candidate = link.get('href') or link.get_text()
        if file_candidate and pattern.search(file_candidate):
            files.append(file_candidate)
    
    # Reverse the file order (assuming the listing order reflects creation/modification order)
    files = list(reversed(files))
    
    file_details = []
    for filename in files:
        file_url = base_url + filename
        try:
            file_response = requests.get(file_url)
            file_response.raise_for_status()
        except Exception as e:
            # Skip file if error occurs
            continue

        # Use the plain text content directly (no decompression needed)
        lines = file_response.text.splitlines()
        # Read the file in reverse to quickly get the last non-empty line
        last_line = None
        for line in reversed(lines):
            if line.strip():
                last_line = line
                break
        if not last_line:
            continue
        tokens = last_line.split()
        if tokens:
            timestamp_token = tokens[0]
            try:
                # Try parsing the timestamp; expected format: YYYYMMDDT%H%M%S.%fZ
                dt = datetime.strptime(timestamp_token, "%Y%m%dT%H%M%S.%fZ")
                formatted_ts = dt.strftime("%Y-%m-%d")
            except Exception as e:
                # If parsing fails, return the raw token
                formatted_ts = timestamp_token
            file_details.append({"file": filename, "timestamp": formatted_ts})
    return None, base_url, file_details

@app.route("/", methods=["GET", "POST"])
def index():
    error = None
    l0_result = None
    l0_date = None
    l0_generated_url = None
    l2_generated_url = None
    l2_file_details = []

    if request.method == "POST":
        selected_site = request.form.get("selected_site")
        if selected_site:
            location, pandora_number = selected_site.split("|")
            # Process L0 directory
            error, l0_generated_url, l0_result, l0_date = get_most_recent_file_L0(location, pandora_number)
            if not l0_result and not error:
                error = "No matching L0 file found."
            # Process L2 directory
            err2, l2_generated_url, l2_file_details = get_l2_file_last_line_dates(location, pandora_number)
            if err2:
                error = err2

    return render_template("index.html", sites=sites, 
                           l0_result=l0_result, l0_date=l0_date, l0_generated_url=l0_generated_url,
                           l2_generated_url=l2_generated_url, l2_file_details=l2_file_details, error=error)

if __name__ == "__main__":
    app.run_server(debug=True)
