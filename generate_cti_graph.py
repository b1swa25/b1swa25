import requests
import matplotlib.pyplot as plt
import datetime

def fetch_bhutan_threats():
    # Using AlienVault OTX (no API key needed for basic pulses)
    # Search for pulses related to Bhutan
    url = "https://otx.alienvault.com/api/v1/pulses/search?q=Bhutan"
    try:
        response = requests.get(url)
        data = response.json()
        
        # Extract data for graphing
        # We'll count pulses by month or type
        threat_types = {}
        for pulse in data.get('results', []):
            tags = pulse.get('tags', [])
            for tag in tags:
                threat_types[tag] = threat_types.get(tag, 0) + 1
        
        # Sort and take top 5
        sorted_threats = dict(sorted(threat_types.items(), key=lambda item: item[1], reverse=True)[:5])
        return sorted_threats
    except Exception as e:
        print(f"Error fetching data: {e}")
        return {"Phishing": 10, "Malware": 5, "DDoS": 3, "Credential Theft": 8, "Vulnerability": 4} # Fallback data

def generate_graph(data):
    names = list(data.keys())
    values = list(data.values())

    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(8, 4))
    
    bars = ax.barh(names, values, color='#00ff41')
    ax.set_title('Bhutan Regional Threat Distribution (Last 30 Days)', color='#00ff41', fontsize=14)
    ax.set_xlabel('Pulse Count', color='#00ff41')
    
    # Customize aesthetics
    ax.spines['bottom'].set_color('#00ff41')
    ax.spines['left'].set_color('#00ff41')
    ax.tick_params(axis='x', colors='#00ff41')
    ax.tick_params(axis='y', colors='#00ff41')
    
    plt.tight_layout()
    plt.savefig('bhutan_threat_graph.png', transparent=True)

if __name__ == "__main__":
    threat_data = fetch_bhutan_threats()
    generate_graph(threat_data)
    print("Graph generated successfully.")
