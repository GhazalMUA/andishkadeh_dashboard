# Configuration for dynamic variables
XPATHS = {
    "accept_cookies": "L2AGLb",
    "chromedriver_path": "/opt/homebrew/bin/chromedriver",
    "search_box": "q",
    "tools_button": "//div[@aria-controls='hdtb-tls']//button", 
    "time_dropdown": "//div[contains(@class, 'KTBKoe') and text()='Any time']",
    "custom_range": "//span[text()='Custom range...']",
    "next_button": "//a[text()='Next']",
    "from_date": "OouJcb",
    "to_date": "rzG2be",
    "submit_button": "g-button",
    "result_container": "div.g",
    "result_link": "a",
    "result_title": "h3",
    "result_preview": "div.VwiC3b",
    "result_datetime": "span.LEwnzc",
}

MY_IGNORED_LIST =['expert', 'experts', 'by-expert', 'people', 'author', 'authors', 'researchers', 'researcher',
                   'event', 'events', 'person', 'book', 'books', 'topic', 'topics', 'archive', 'series', 'region',
                   'program', 'programs', 'issue', 'content-type', 'job-opportunity', 'about', 'tag', 'company',
                   'search', 'category'
                   'contact', 'privacy', 'terms', 'donate', 'subscribe', 'login', 'register'
                   'twitter.com', 'facebook.com', 'linkedin.com', 'youtube.com'
]

# List of categories/types (expand this as needed)
CONTENT_CATEGORIES = ["blog", "news", "forum", "article", "podcast", "video", "centers","articles"
                    "interview", "media", "events", "event", "program", "programs", "projects",
                    "expert", "experts", "quiz", "op-ed", "timeline", "testimony", "centers", 
                    "briefs", "testimonies", "report", "reports", "publications", "profile", "essay", 
                    "chapter", "Q&A", "book", "grants", "summery", "feature", "series", "newsletter", "topics", 
                    "china-center", "corruption", "defense-strategy", "democracy", "domestic-policy",
                    "economics", "foreign-policy", "global-economy", "hudson-welcomes-congressman-mike-gallagher",
                    "human-rights", "information-technology", "international-organizations", "missile-defense",
                    "national-security-defense", "node", "policycenters", "politics-government", "religious-freedom",
                    "security-alliances", "supply-chains", "terrorism","commentary", "issue",
]


COUNTRY_LIST = [
    'afghanistan', 'albania', 'algeria', 'andorra', 'angola', 'antigua-and-barbuda',
    'argentina', 'armenia', 'australia', 'austria', 'azerbaijan', 'bahamas', 'bahrain',
    'bangladesh', 'barbados', 'belarus', 'belgium', 'belize', 'benin', 'bhutan', 'bolivia',
    'bosnia-and-herzegovina', 'botswana', 'brazil', 'brunei', 'bulgaria', 'burkina-faso', 'burundi',
    'cabo-verde', 'cambodia', 'cameroon', 'canada', 'central-african-republic', 'chad',
    'chile', 'china', 'colombia', 'comoros', 'costa-rica', 'croatia', 'cuba', 'cyprus',
    'czech-republic', 'democratic-republic-of-the-congo', 'denmark', 'djibouti', 'dominica',
    'dominican-republic', 'ecuador', 'egypt', 'el-salvador', 'equatorial-guinea', 'eritrea',
    'estonia', 'eswatini', 'ethiopia', 'fiji', 'finland', 'france', 'gabon', 'gambia',
    'georgia', 'germany', 'ghana', 'greece', 'grenada', 'guatemala', 'guinea', 'guinea-bissau',
    'haiti', 'honduras', 'hungary', 'iceland', 'india', 'indonesia', 'iran', 'iraq', 'ireland',
    'israel', 'italy', 'jamaica', 'japan', 'jordan', 'kazakhstan', 'kenya', 'kiribati', 'kosovo',
    'kuwait', 'kyrgyzstan', 'laos', 'latvia', 'lebanon', 'lesotho', 'liberia', 'libya',
    'liechtenstein', 'lithuania', 'luxembourg', 'madagascar', 'malawi', 'malaysia', 'maldives',
    'mali', 'malta', 'marshall-islands', 'mauritania', 'mauritius', 'mexico', 'micronesia',
    'moldova', 'monaco', 'mongolia', 'montenegro', 'morocco', 'mozambique', 'myanmar-(burma)',
    'namibia', 'nauru', 'nepal', 'netherlands', 'new-zealand', 'nicaragua', 'niger', 'nigeria',
    'north-korea', 'north-macedonia', 'norway', 'oman', 'pakistan', 'palau', 'palestine',
    'panama', 'papua-new-guinea', 'paraguay', 'peru', 'philippines', 'poland', 'portugal',
    'qatar', 'republic-of-the-congo', 'romania', 'russia', 'rwanda', 'saint-kitts-and-nevis',
    'saint-lucia', 'saint-vincent-and-the-grenadines', 'san-marino', 'sao-tome-and-principe',
    'saudi-arabia', 'senegal', 'serbia', 'seychelles', 'sierra-leone', 'singapore', 'slovakia',
    'slovenia', 'solomon-islands', 'somalia', 'south-africa', 'south-korea', 'south-sudan',
    'sri-lanka', 'sudan', 'suriname', 'sweden', 'switzerland', 'syria', 'taiwan', 'tajikistan',
    'tanzania', 'thailand', 'timor-leste-(east-timor)', 'togo', 'trinidad-and-tobago', 'tunisia',
    'turkey', 'turkmenistan', 'tuvalu', 'uganda', 'ukraine', 'united-arab-emirates',
    'united-kingdom', 'united-states', 'uruguay', 'uzbekistan', 'vanuatu', 'vatican-city',
    'venezuela', 'vietnam', 'yemen', 'zambia', 'zimbabwe', 'africa', 'asia', 'europe',
    'north-america', 'south-america', 'oceania', 'middle-east', 'southeast-asia', 'central-asia',
    'south-asia', 'east-asia', 'northern-europe', 'southern-europe', 'western-europe',
    'eastern-europe', 'sub-saharan-africa', 'caribbean', 'latin-america', 'central-america',
    'northern-america', 'australasia', 'pacific-islands', 'southeast-europe', 'central-europe',
    'baltic-states'
]