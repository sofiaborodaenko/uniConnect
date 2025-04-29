# uniConnect: A Centralized Hub for College Events at UofT
## A Centralized Hub for College Events at UofT

UniConnect was created to solve a common but overlooked issue at the University of Toronto: the fragmentation of college event information. With events scattered across various posters, Instagram pages, and internal mailing lists, many students are unaware of what’s happening outside their college, even though many of these events are open to everyone. 
So Dawson Li, Yi-ting Chang, Japleen Kaur and I built a unified web platform that scrapes event data from six major UofT colleges, organizes the information using an optimized tree structure, and allows users to filter, sort, and explore events dynamically through a modern Flask-based interface. The platform also includes a recommendation system that tailors results based on user preferences such as college, faculty, and event type.

## 🧠 Key Features
* Web Scraping + LLM Data Extraction: Automatically pulls event data from six UofT college websites using BeautifulSoup, Selenium, and custom LLM pipelines.

* Tree-Based Event Structure: Efficiently stores events by day, college, and category for fast filtering and searching.

* Dynamic Filtering & Sorting: Instantly filter events by weekday, category, or college and sort by date.

* User Profile & Recommendations: Tailored event suggestions based on student preferences using a weighted scoring system.

* Clean Web Interface: Flask-powered frontend with Jinja templates, custom filters, and responsive interactivity.

