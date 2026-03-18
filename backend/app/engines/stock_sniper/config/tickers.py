"""
Stock Tickers Watchlist

A diversified list of 436 unique stocks across multiple sectors for the Sniper Bot to scan.
Organised by sector for better diversification and risk management.
"""

# =============================================================================
# TECHNOLOGY (40 stocks)
# =============================================================================
TECHNOLOGY = [
    'AAPL',  # Apple Inc.
    'MSFT',  # Microsoft Corporation
    'GOOGL', # Alphabet Inc. (Google)
    'META',  # Meta Platforms (Facebook)
    'NVDA',  # NVIDIA Corporation
    'AMD',   # Advanced Micro Devices
    'INTC',  # Intel Corporation
    'CRM',   # Salesforce Inc.
    'ADBE',  # Adobe Inc.
    'ORCL',  # Oracle Corporation
    'CSCO',  # Cisco Systems
    'IBM',   # IBM Corporation
    'SHOP',  # Shopify Inc.
    'PYPL',  # PayPal Holdings
    'UBER',  # Uber Technologies
    'LYFT',  # Lyft Inc.
    'SNAP',  # Snap Inc.
    'TWLO',  # Twilio Inc.
    'DOCU',  # DocuSign Inc.
    'ZM',    # Zoom Video Communications
    'TEAM',  # Atlassian Corporation
    'DDOG',  # Datadog Inc.
    'NET',   # Cloudflare Inc.
    'CRWD',  # CrowdStrike Holdings
    'OKTA',  # Okta Inc.
    'MDB',   # MongoDB Inc.
    'SNOW',  # Snowflake Inc.
    'PLTR',  # Palantir Technologies
    'RBLX',  # Roblox Corporation
    'U',     # Unity Software
    'COIN',  # Coinbase Global
    'ROKU',  # Roku Inc.
    'PINS',  # Pinterest Inc.
    'SPOT',  # Spotify Technology
    'DASH',  # DoorDash Inc.
    'ABNB',  # Airbnb Inc.
    'BABA',  # Alibaba Group
    'JD',    # JD.com Inc.
    'BIDU',  # Baidu Inc.
]

# =============================================================================
# FINANCE (25 stocks)
# =============================================================================
FINANCE = [
    'JPM',   # JPMorgan Chase
    'BAC',   # Bank of America
    'WFC',   # Wells Fargo
    'C',     # Citigroup
    'GS',    # Goldman Sachs
    'MS',    # Morgan Stanley
    'V',     # Visa Inc.
    'MA',    # Mastercard Inc.
    'PYPL',  # PayPal Holdings
    'SQ',    # Block Inc.
    'SOFI',  # SoFi Technologies
    'AFRM',  # Affirm Holdings
    'HOOD',  # Robinhood Markets
    'CME',   # CME Group
    'ICE',   # Intercontinental Exchange
    'MCO',   # Moody's Corporation
    'MSCI',  # MSCI Inc.
    'TROW',  # T. Rowe Price
    'BEN',   # Franklin Resources
    'IVZ',   # Invesco Ltd.
    'ALLY',  # Ally Financial
    'RF',    # Regions Financial
    'KEY',   # KeyCorp
    'FITB',  # Fifth Third Bancorp
    'HBAN',  # Huntington Bancshares
]

# =============================================================================
# HEALTHCARE (30 stocks)
# =============================================================================
HEALTHCARE = [
    'JNJ',   # Johnson & Johnson
    'UNH',   # UnitedHealth Group
    'PFE',   # Pfizer Inc.
    'ABBV',  # AbbVie Inc.
    'MRK',   # Merck & Co.
    'LLY',   # Eli Lilly
    'TMO',   # Thermo Fisher Scientific
    'ABT',   # Abbott Laboratories
    'DHR',   # Danaher Corporation
    'BMY',   # Bristol-Myers Squibb
    'NVO',   # Novo Nordisk
    'MRNA',  # Moderna Inc.
    'ZTS',   # Zoetis Inc.
    'BDX',   # Becton Dickinson
    'ELV',   # Elevance Health
    'IDXX',  # IDEXX Laboratories
    'IQV',   # IQVIA Holdings
    'A',     # Agilent Technologies
    'RMD',   # ResMed Inc.
    'DXCM',  # DexCom Inc.
    'ALGN',  # Align Technology
    'EW',    # Edwards Lifesciences
    'HCA',   # HCA Healthcare
    'CNC',   # Centene Corporation
    'MOH',   # Molina Healthcare
    'ZBH',   # Zimmer Biomet
    'HOLX',  # Hologic Inc.
    'PODD',  # Insulet Corporation
    'TECH',  # Bio-Techne Corporation
    'VTRS',  # Viatris Inc.
]

# =============================================================================
# CONSUMER (35 stocks)
# =============================================================================
CONSUMER = [
    'AMZN',  # Amazon.com Inc.
    'TSLA',  # Tesla Inc.
    'WMT',   # Walmart Inc.
    'HD',    # Home Depot
    'NKE',   # Nike Inc.
    'MCD',   # McDonald's Corporation
    'SBUX',  # Starbucks Corporation
    'TGT',   # Target Corporation
    'COST',  # Costco Wholesale
    'CVS',   # CVS Health
    'KR',    # Kroger Company
    'BBY',   # Best Buy
    'EBAY',  # eBay Inc.
    'ETSY',  # Etsy Inc.
    'W',     # Wayfair Inc.
    'CHWY',  # Chewy Inc.
    'LULU',  # Lululemon Athletica
    'UAA',   # Under Armour
    'CROX',  # Crocs Inc.
    'DECK',  # Deckers Outdoor
    'RL',    # Ralph Lauren
    'CPRI',  # Capri Holdings
    'TPR',   # Tapestry Inc.
    'ULTA',  # Ulta Beauty
    'EL',    # Estee Lauder
    'ANF',   # Abercrombie & Fitch
    'M',     # Macy's Inc.
    'KSS',   # Kohl's Corporation
    'PLNT',  # Planet Fitness
    'LEVI',  # Levi Strauss
    'COTY',  # Coty Inc.
    'RIVN',  # Rivian Automotive
]

# =============================================================================
# ENERGY & INDUSTRIALS (30 stocks)
# =============================================================================
ENERGY_INDUSTRIALS = [
    'XOM',   # Exxon Mobil
    'CVX',   # Chevron Corporation
    'BA',    # Boeing Company
    'CAT',   # Caterpillar Inc.
    'GE',    # General Electric
    'DE',    # Deere & Company
    'UPS',   # United Parcel Service
    'OXY',   # Occidental Petroleum
    'HAL',   # Halliburton
    'BKR',   # Baker Hughes
    'DVN',   # Devon Energy
    'FANG',  # Diamondback Energy
    'APA',   # APA Corporation
    'OKE',   # ONEOK Inc.
    'WMB',   # Williams Companies
    'KMI',   # Kinder Morgan
    'TRP',   # TC Energy
    'GD',    # General Dynamics
    'NOC',   # Northrop Grumman
    'LHX',   # L3Harris Technologies
    'TDG',   # TransDigm Group
    'CARR',  # Carrier Global
    'OTIS',  # Otis Worldwide
    'PCAR',  # PACCAR Inc.
    'IR',    # Ingersoll Rand
    'ROK',   # Rockwell Automation
    'PH',    # Parker Hannifin
    'FTV',   # Fortive Corporation
]

# =============================================================================
# CONSUMER STAPLES & MATERIALS (30 stocks)
# =============================================================================
STAPLES_MATERIALS = [
    'PG',    # Procter & Gamble
    'KO',    # Coca-Cola Company
    'PEP',   # PepsiCo Inc.
    'PM',    # Philip Morris International
    'CL',    # Colgate-Palmolive
    'COST',  # Costco Wholesale
    'FCX',   # Freeport-McMoRan (Materials)
    'MO',    # Altria Group
    'MDLZ',  # Mondelez International
    'KHC',   # Kraft Heinz
    'GIS',   # General Mills
    'K',     # Kellogg Company
    'CAG',   # Conagra Brands
    'HSY',   # Hershey Company
    'CPB',   # Campbell Soup
    'SJM',   # J.M. Smucker
    'TSN',   # Tyson Foods
    'HRL',   # Hormel Foods
    'KMB',   # Kimberly-Clark
    'CHD',   # Church & Dwight
    'CLX',   # Clorox Company
    'TAP',   # Molson Coors
    'STZ',   # Constellation Brands
    'LW',    # Lamb Weston
    'GOLD',  # Barrick Gold
    'NUE',   # Nucor Corporation
    'STLD',  # Steel Dynamics
    'AA',    # Alcoa Corporation
]

# =============================================================================
# ADDITIONAL TECHNOLOGY (35 stocks)
# =============================================================================
TECHNOLOGY_2 = [
    'AVGO',  # Broadcom Inc.
    'QCOM',  # Qualcomm Inc.
    'TXN',   # Texas Instruments
    'AMAT',  # Applied Materials
    'MU',    # Micron Technology
    'LRCX',  # Lam Research
    'KLAC',  # KLA Corporation
    'SNPS',  # Synopsys Inc.
    'CDNS',  # Cadence Design Systems
    'MCHP',  # Microchip Technology
    'PANW',  # Palo Alto Networks
    'FTNT',  # Fortinet Inc.
    'NOW',   # ServiceNow Inc.
    'WDAY',  # Workday Inc.
    'ZS',    # Zscaler Inc.
    'HUBS',  # HubSpot Inc.
    'RNG',   # RingCentral Inc.
    'FIVE',  # Five9 Inc.
    'VEEV',  # Veeva Systems
    'ESTC',  # Elastic N.V.
    'PATH',  # UiPath Inc.
    'BILL',  # Bill.com Holdings
    'S',     # SentinelOne Inc.
    'RPD',   # Rapid7 Inc.
    'TENB',  # Tenable Holdings
    'CYBR',  # CyberArk Software
    'DT',    # Dynatrace Inc.
    'GTLB',  # GitLab Inc.
    'FROG',  # JFrog Ltd.
    'CFLT',  # Confluent Inc.
    'MNDY',  # Monday.com Ltd.
    'IOT',   # Samsara Inc.
    'PCOR',  # Procore Technologies
    'APP',   # AppLovin Corporation
]

# =============================================================================
# ADDITIONAL FINANCE (25 stocks)
# =============================================================================
FINANCE_2 = [
    'BRK-B', # Berkshire Hathaway
    'BLK',   # BlackRock Inc.
    'SCHW',  # Charles Schwab
    'AXP',   # American Express
    'SPGI',  # S&P Global
    'USB',   # U.S. Bancorp
    'TFC',   # Truist Financial
    'PNC',   # PNC Financial Services
    'COF',   # Capital One Financial
    'AIG',   # American International Group
    'MET',   # MetLife Inc.
    'PRU',   # Prudential Financial
    'ALL',   # Allstate Corporation
    'TRV',   # Travelers Companies
    'PGR',   # Progressive Corporation
    'CB',    # Chubb Limited
    'AFL',   # Aflac Inc.
    'HIG',   # Hartford Financial
    'CMA',   # Comerica Inc.
    'MTB',   # M&T Bank Corporation
    'CFG',   # Citizens Financial Group
    'ZION',  # Zions Bancorporation
    'WRB',   # W.R. Berkley Corporation
    'GL',    # Globe Life Inc.
    'RJF',   # Raymond James Financial
]

# =============================================================================
# ADDITIONAL HEALTHCARE (30 stocks)
# =============================================================================
HEALTHCARE_2 = [
    'AMGN',  # Amgen Inc.
    'GILD',  # Gilead Sciences
    'BIIB',  # Biogen Inc.
    'REGN',  # Regeneron Pharmaceuticals
    'VRTX',  # Vertex Pharmaceuticals
    'CI',    # Cigna Corporation
    'CVS',   # CVS Health Corporation
    'HUM',   # Humana Inc.
    'ISRG',  # Intuitive Surgical
    'MDT',   # Medtronic PLC
    'BSX',   # Boston Scientific
    'SYK',   # Stryker Corporation
    'ILMN',  # Illumina Inc.
    'INCY',  # Incyte Corporation
    'EXAS',  # Exact Sciences
    'IONS',  # Ionis Pharmaceuticals
    'BMRN',  # BioMarin Pharmaceutical
    'ALNY',  # Alnylam Pharmaceuticals
    'NBIX',  # Neurocrine Biosciences
    'EXEL',  # Exelixis Inc.
    'UTHR',  # United Therapeutics
    'JAZZ',  # Jazz Pharmaceuticals
    'ARWR',  # Arrowhead Pharmaceuticals
    'RGEN',  # Repligen Corporation
    'PTCT',  # PTC Therapeutics
    'RARE',  # Ultragenyx Pharmaceutical
    'FOLD',  # Amicus Therapeutics
    'DNLI',  # Denali Therapeutics
]

# =============================================================================
# ADDITIONAL CONSUMER & RETAIL (40 stocks)
# =============================================================================
CONSUMER_2 = [
    'DIS',   # Walt Disney Company
    'NFLX',  # Netflix Inc.
    'CMCSA', # Comcast Corporation
    'LOW',   # Lowe's Companies
    'TJX',   # TJX Companies
    'BKNG',  # Booking Holdings
    'ABNB',  # Airbnb Inc.
    'MAR',   # Marriott International
    'GM',    # General Motors
    'F',     # Ford Motor Company
    'YUM',   # Yum! Brands
    'CMG',   # Chipotle Mexican Grill
    'ROST',  # Ross Stores
    'DG',    # Dollar General
    'DLTR',  # Dollar Tree
    'WBD',   # Warner Bros. Discovery
    'FOX',   # Fox Corporation
    'LVS',   # Las Vegas Sands
    'MGM',   # MGM Resorts International
    'WYNN',  # Wynn Resorts
    'HLT',   # Hilton Worldwide
    'H',     # Hyatt Hotels
    'RCL',   # Royal Caribbean
    'CCL',   # Carnival Corporation
    'NCLH',  # Norwegian Cruise Line
    'LYV',   # Live Nation Entertainment
    'MSGS',  # Madison Square Garden Sports
    'DKNG',  # DraftKings Inc.
    'PENN',  # Penn Entertainment
    'LCID',  # Lucid Group
    'QSR',   # Restaurant Brands International
    'DPZ',   # Domino's Pizza
    'WING',  # Wingstop Inc.
    'TXRH',  # Texas Roadhouse
    'BLMN',  # Bloomin' Brands
    'JACK',  # Jack in the Box
]

# =============================================================================
# ADDITIONAL ENERGY & INDUSTRIALS (30 stocks)
# =============================================================================
ENERGY_INDUSTRIALS_2 = [
    'SLB',   # Schlumberger
    'MPC',   # Marathon Petroleum
    'PSX',   # Phillips 66
    'VLO',   # Valero Energy
    'EOG',   # EOG Resources
    'COP',   # ConocoPhillips
    'LMT',   # Lockheed Martin
    'RTX',   # Raytheon Technologies
    'HON',   # Honeywell International
    'MMM',   # 3M Company
    'EMR',   # Emerson Electric
    'ETN',   # Eaton Corporation
    'ITW',   # Illinois Tool Works
    'CNI',   # Canadian National Railway
    'CP',    # Canadian Pacific Railway
    'GWW',   # W.W. Grainger
    'FAST',  # Fastenal Company
    'WM',    # Waste Management
    'RSG',   # Republic Services
    'BLDR',  # Builders FirstSource
    'VMC',   # Vulcan Materials
    'MLM',   # Martin Marietta Materials
    'PWR',   # Quanta Services
    'EME',   # EMCOR Group
    'MTZ',   # MasTec Inc.
    'URI',   # United Rentals
    'HRI',   # Herc Holdings
    'RBA',   # RB Global
    'CHRW',  # C.H. Robinson Worldwide
]

# =============================================================================
# TELECOMMUNICATIONS & UTILITIES (25 stocks)
# =============================================================================
TELECOM_UTILITIES = [
    'T',     # AT&T Inc.
    'VZ',    # Verizon Communications
    'TMUS',  # T-Mobile US
    'NEE',   # NextEra Energy
    'DUK',   # Duke Energy
    'SO',    # Southern Company
    'D',     # Dominion Energy
    'AEP',   # American Electric Power
    'EXC',   # Exelon Corporation
    'XEL',   # Xcel Energy
    'SRE',   # Sempra Energy
    'ED',    # Consolidated Edison
    'ES',    # Eversource Energy
    'DTE',   # DTE Energy
    'PEG',   # Public Service Enterprise
    'WEC',   # WEC Energy Group
    'AWK',   # American Water Works
    'AEE',   # Ameren Corporation
    'PPL',   # PPL Corporation
    'FE',    # FirstEnergy Corporation
    'CNP',   # CenterPoint Energy
    'ETR',   # Entergy Corporation
    'CMS',   # CMS Energy
    'NI',    # NiSource Inc.
    'LNT',   # Alliant Energy
]

# =============================================================================
# REAL ESTATE & REITS (25 stocks)
# =============================================================================
REAL_ESTATE = [
    'AMT',   # American Tower Corporation
    'PLD',   # Prologis Inc.
    'CCI',   # Crown Castle Inc.
    'EQIX',  # Equinix Inc.
    'PSA',   # Public Storage
    'SPG',   # Simon Property Group
    'O',     # Realty Income Corporation
    'WELL',  # Welltower Inc.
    'DLR',   # Digital Realty Trust
    'SBAC',  # SBA Communications
    'AVB',   # AvalonBay Communities
    'EQR',   # Equity Residential
    'VTR',   # Ventas Inc.
    'ARE',   # Alexandria Real Estate
    'INVH',  # Invitation Homes
    'EXR',   # Extra Space Storage
    'CBRE',  # CBRE Group
    'UDR',   # UDR Inc.
    'ESS',   # Essex Property Trust
    'MAA',   # Mid-America Apartment
    'KIM',   # Kimco Realty
    'REG',   # Regency Centers
    'BXP',   # Boston Properties
    'HST',   # Host Hotels & Resorts
]

# =============================================================================
# TRANSPORTATION & LOGISTICS (20 stocks)
# =============================================================================
TRANSPORTATION = [
    'FDX',   # FedEx Corporation
    'DAL',   # Delta Air Lines
    'UAL',   # United Airlines
    'AAL',   # American Airlines
    'LUV',   # Southwest Airlines
    'NSC',   # Norfolk Southern
    'CSX',   # CSX Corporation
    'UNP',   # Union Pacific
    'JBHT',  # J.B. Hunt Transport
    'KNX',   # Knight-Swift Transportation
    'ODFL',  # Old Dominion Freight
    'XPO',   # XPO Logistics
    'R',     # Ryder System
    'EXPD',  # Expeditors International
    'JBLU',  # JetBlue Airways
    'ALK',   # Alaska Air Group
    'SNDR',  # Schneider National
    'WERN',  # Werner Enterprises
]

# =============================================================================
# MATERIALS & CHEMICALS (20 stocks)
# =============================================================================
MATERIALS_2 = [
    'NEM',   # Newmont Corporation
    'DOW',   # Dow Inc.
    'DD',    # DuPont de Nemours
    'APD',   # Air Products and Chemicals
    'ECL',   # Ecolab Inc.
    'LIN',   # Linde PLC
    'SHW',   # Sherwin-Williams
    'PPG',   # PPG Industries
    'LYB',   # LyondellBasell Industries
    'CE',    # Celanese Corporation
    'EMN',   # Eastman Chemical
    'ALB',   # Albemarle Corporation
    'FMC',   # FMC Corporation
    'CF',    # CF Industries
    'MOS',   # Mosaic Company
    'IFF',   # International Flavors
    'CTVA',  # Corteva Inc.
    'PKG',   # Packaging Corp of America
    'IP',    # International Paper
]

# =============================================================================
# SEMICONDUCTORS & CHIPS (20 stocks)
# =============================================================================
SEMICONDUCTORS = [
    'ADI',   # Analog Devices
    'NXPI',  # NXP Semiconductors
    'ON',    # ON Semiconductor
    'MPWR',  # Monolithic Power Systems
    'SWKS',  # Skyworks Solutions
    'QRVO',  # Qorvo Inc.
    'MRVL',  # Marvell Technology
    'SLAB',  # Silicon Laboratories
    'CRUS',  # Cirrus Logic
    'SYNA',  # Synaptics Inc.
    'DIOD',  # Diodes Incorporated
    'WOLF',  # Wolfspeed Inc.
    'POWI',  # Power Integrations
    'SITM',  # SiTime Corporation
    'ALGM',  # Allegro MicroSystems
    'SMTC',  # Semtech Corporation
    'LITE',  # Lumentum Holdings
    'RMBS',  # Rambus Inc.
    'INDI',  # indie Semiconductor
    'PLAB',  # Photronics Inc.
]

# =============================================================================
# COMBINED WATCHLIST (436 unique stocks total)
# =============================================================================
WATCHLIST = (
    TECHNOLOGY +
    FINANCE +
    HEALTHCARE +
    CONSUMER +
    ENERGY_INDUSTRIALS +
    STAPLES_MATERIALS +
    TECHNOLOGY_2 +
    FINANCE_2 +
    HEALTHCARE_2 +
    CONSUMER_2 +
    ENERGY_INDUSTRIALS_2 +
    TELECOM_UTILITIES +
    REAL_ESTATE +
    TRANSPORTATION +
    MATERIALS_2 +
    SEMICONDUCTORS
)

# Remove duplicates (safety check for tickers appearing in multiple categories)
WATCHLIST = list(dict.fromkeys(WATCHLIST))

# Verify total count after deduplication
assert len(WATCHLIST) == 436, f"Expected 436 unique tickers, got {len(WATCHLIST)}"

# =============================================================================
# SECTOR MAPPING (for reporting)
# =============================================================================
SECTOR_MAP = {
    **{ticker: 'Technology' for ticker in TECHNOLOGY},
    **{ticker: 'Finance' for ticker in FINANCE},
    **{ticker: 'Healthcare' for ticker in HEALTHCARE},
    **{ticker: 'Consumer' for ticker in CONSUMER},
    **{ticker: 'Energy/Industrials' for ticker in ENERGY_INDUSTRIALS},
    **{ticker: 'Staples/Materials' for ticker in STAPLES_MATERIALS},
    **{ticker: 'Technology' for ticker in TECHNOLOGY_2},
    **{ticker: 'Finance' for ticker in FINANCE_2},
    **{ticker: 'Healthcare' for ticker in HEALTHCARE_2},
    **{ticker: 'Consumer' for ticker in CONSUMER_2},
    **{ticker: 'Energy/Industrials' for ticker in ENERGY_INDUSTRIALS_2},
    **{ticker: 'Telecom/Utilities' for ticker in TELECOM_UTILITIES},
    **{ticker: 'Real Estate' for ticker in REAL_ESTATE},
    **{ticker: 'Transportation' for ticker in TRANSPORTATION},
    **{ticker: 'Materials' for ticker in MATERIALS_2},
    **{ticker: 'Semiconductors' for ticker in SEMICONDUCTORS},
}

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_all_tickers():
    """Get the complete watchlist of tickers."""
    return WATCHLIST.copy()

def get_tickers_by_sector(sector_name):
    """
    Get tickers for a specific sector.

    Args:
        sector_name: One of 'Technology', 'Finance', 'Healthcare', 'Consumer',
                     'Energy/Industrials', 'Staples/Materials'

    Returns:
        List of tickers in that sector
    """
    sector_lists = {
        'Technology': TECHNOLOGY,
        'Finance': FINANCE,
        'Healthcare': HEALTHCARE,
        'Consumer': CONSUMER,
        'Energy/Industrials': ENERGY_INDUSTRIALS,
        'Staples/Materials': STAPLES_MATERIALS,
    }
    return sector_lists.get(sector_name, []).copy()

def get_sector(ticker):
    """Get the sector for a specific ticker."""
    return SECTOR_MAP.get(ticker, 'Unknown')

def get_ticker_count():
    """Get total number of tickers in watchlist."""
    return len(WATCHLIST)

def get_sector_distribution():
    """Get count of tickers per sector."""
    distribution = {}
    for ticker, sector in SECTOR_MAP.items():
        distribution[sector] = distribution.get(sector, 0) + 1
    return distribution


if __name__ == '__main__':
    # Print watchlist summary
    print(f"📊 Stock Sniper Watchlist")
    print(f"{'='*60}")
    print(f"Total Tickers: {get_ticker_count()}\n")

    print("Sector Distribution:")
    for sector, count in get_sector_distribution().items():
        print(f"  • {sector}: {count} stocks")

    print(f"\n{'='*60}")
    print("Complete Watchlist:")
    print(", ".join(WATCHLIST))
