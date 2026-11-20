import requests
import matplotlib.pyplot as plt
import os

def fetch_bhutan_threats():
    api_key = os.environ.get('OTX_API_KEY')
    if not api_key:
        raise RuntimeError('Set the OTX_API_KEY environment variable to fetch threat intelligence.')

    url = "https://otx.alienvault.com/api/v1/search/pulses"
    response = requests.get(
        url,
        params={'q': 'Bhutan'},
        headers={'X-OTX-API-KEY': api_key},
        timeout=30
    )
    response.raise_for_status()
    data = response.json()

    threat_types = {}
    for pulse in data.get('results', []):
        for tag in pulse.get('tags', []):
            threat_types[tag] = threat_types.get(tag, 0) + 1

    return dict(sorted(threat_types.items(), key=lambda item: item[1], reverse=True)[:5])

def generate_graph(data):
    names = list(data.keys())
    values = list(data.values())

    background = '#0d1117'
    foreground = '#c9d1d9'
    accent = '#39d0c3'
    fig, ax = plt.subplots(figsize=(9, 4.5), facecolor=background)
    ax.set_facecolor(background)
    ax.set_title('Bhutan-Related Threat Intelligence Tags', color=foreground, fontsize=15, pad=18)

    if names:
        bars = ax.barh(names, values, color=accent, height=0.65)
        ax.invert_yaxis()
        ax.set_xlabel('Pulse tag occurrences', color=foreground)
        ax.bar_label(bars, padding=6, color=foreground)
        ax.set_xlim(0, max(values) * 1.15)
        ax.spines['bottom'].set_color('#30363d')
        ax.spines['left'].set_color('#30363d')
        ax.tick_params(axis='x', colors=foreground)
        ax.tick_params(axis='y', colors=foreground)
        ax.xaxis.grid(True, color='#21262d', linewidth=0.8)
        ax.set_axisbelow(True)
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
    else:
        ax.set_axis_off()
        ax.text(
            0.5, 0.5, 'No tagged threats found in the latest feed.',
            color=foreground, ha='center', va='center', transform=ax.transAxes,
            fontsize=12
        )

    fig.tight_layout(pad=2)
    fig.savefig('bhutan_threat_graph.png', dpi=160, facecolor=background)
    plt.close(fig)

if __name__ == "__main__":
    threat_data = fetch_bhutan_threats()
    generate_graph(threat_data)
    print("Graph generated successfully.")
