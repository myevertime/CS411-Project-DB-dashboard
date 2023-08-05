### Title
University Explorer - A Comprehensive Dashboard for Computer Science Students

### Purpose
We developed a web-based dashboard designed to assist students who are aspiring to pursue a computer science major. The primary motivation behind this project is to address the lack of comprehensive information available about faculty and publications in various universities, which often hinders students from making well-informed decisions. Our team aims to create an interactive web dashboard that provides all the necessary details to help students choose the right university based on their preferences and interests.

### Demo
https://mediaspace.illinois.edu/media/t/1_fh4nxxxa

### Installation
To install the University Explorer application, follow these steps:

1. Clone this repository.
2. Install Python dependencies: pip install -r requirements.txt
3. Start MySQL Server, MongoDB, and Neo4j databases.
4. Configure SERP and OpenAI API credentials in credentials.py.
	*The web server runs without any issues, even if the API keys are not provided.*
5. Navigate to the project directory and run app.py.
6. Access the application through your web browser at http://127.0.0.1:8050.

<hr>

### Usage
After the web browser successfully launches, the webpage will present a welcoming top banner that includes the dashboard's title and description. Below this banner, three KPI charts are shown, indicating the count of professors, universities, and publication records in the backend database. This provides users with an overview of the database size prior to utilizing the application.

The main body of the dashboard consists of three sections: "Search By Areas," "Search By Professor," and "Search by University."

**In the "Search By Areas" section**, users can choose an area of interest and simultaneously view closely matched faculty and university results. Two tables are sorted based on the match score, referred to as 'KRC,' which calculates the keyword-relevant score by summing up the product of the number of citations of a publication and the number of publications authored by a professor. If the user wants an alternative area of interest, he/she can input a new keyword into the dashboard in the below section.

**Within the "Search By Professor" section**, users can search for a particular professor's name using the provided dropdown menu. The dashboard will then exhibit a concise profile of the professor, encompassing simple network information. The interactive network graph enables users to explore the immediate connections surrounding the chosen professor. Furthermore, the "Professor Section" offers the most recent publications linked to the selected professor, along with a summary crafted by ChatGPT to provide an overview of the professor's profile.

**In the "Search By University Section,"** you have the option to select a specific university from the dropdown menu. Once a university is chosen, the dashboard will dynamically display relevant visualizations associated with the selected institution. A pie chart provides an overview of the key domains within the university based on the top faculties they have. The pie chart showcases the distribution of faculties across various domains, and the hover text provides additional details, such as the number of top faculties in each domain and the combined Knowledge Representation Coefficient (KRC) for the domain. In addition, a bar chart presents the top 5 most popular publications associated with the university's faculties. By clicking on the bars, you can access detailed information about each publication, including its title, venue, year, and the name of the faculty member associated with it. Lastly, a line chart illustrates the publication trend over the last 10 years for the selected university. This line chart provides insights into the university's research output over time, helping to identify any noticeable trends or patterns in publication activity.

Finally, it is important to note that the database may occasionally house inaccurate or outdated records. If users come across such information, they have the option to report them by supplying accurate data. Upon clicking the "Submit" button, the backend system will be promptly updated to reflect the corrected information, and a confirmation pop-up will subsequently appear.

<hr>

### Design
The University Explorer dashboard boasts a clean and visually appealing design, enhancing the overall user experience. We have organized the screen into four distinct sections, each delineated by its own boundary, allowing users to easily perceive their separation.

Primarily, the KPI charts are positioned at the top of the web content, offering users a quick overview of the database size. This visual representation aids users in assessing the potential utility of the dashboard, as database size can influence its relevance.

To ensure an optimized layout, we have allocated varying sizes to each section, considering the differing number of components and chart dimensions they contain. This approach guarantees that sections with numerous charts or larger chart sizes receive ample space, providing users with a comprehensive layout experience.

Moreover, we have strategically placed filters at the top of each section, creating an intuitive user interface that encourages interaction and hints at the possibility of section-specific updates in response to filter usage.

The comprehensive architecture is explained in detail in the preceding section: Usage.

<hr>

### Implementation
The implementation of the Academic Research Exploration Tool involved a variety of technologies and libraries. We organized them into Frontend, Backend, and Database components:

* Frontend:
	* Language
		* Python
			- Dash Framework:
				- The main framework used is Dash, a Python web application framework developed by Plotly. Dash allows for the creation of interactive web applications using pure Python, making it straightforward to integrate data visualization and user controls.
			- Plotly:
				- Plotly, a graphing library has been employed for creating interactive and dynamic visualizations within the dashboard. It provides a wide range of chart types and customization options to present data effectively. 
			- Dash Cytoscape:
				- Dash Cytoscape is an extension of Dash that enables the integration of Cytoscape.js, a powerful graph visualization library. Dash Cytoscape has been utilized to display network graphs of faculty members and their academic relationships. 
		- HTML, CSS, and JavaScript:
			- Custom HTML, CSS, and JavaScript codes have been employed for styling and customizing the appearance and layout of the dashboard. These technologies enhance the user interface and improve the overall user experience.
- Backend:
	- MySQL Connector:
		- The MySQL Connector library has been used to establish a connection to the MySQL database, enabling data retrieval and manipulation from the faculty, publication, and university tables.
	- PyMongo:
		- PyMongo, the official MongoDB driver for Python, has been employed to interact with the MongoDB database. PyMongo facilitates data retrieval and storage related to faculty members' information and publication data.
	- Neo4j Connector:
		- The Neo4j Connector library has been utilized to establish a connection to the Neo4j graph database. It enables the retrieval and processing of network data, contributing to the creation of faculty collaboration graphs.
	- OpenAI API:
		- The OpenAI API has been integrated into the tool to enable the utilization of ChatGPT. It provides a summary of faculty information.
	- SERP API:
		- The SERP API has been used to access Google Scholar data, enriching the dashboard with external information about recent publications.
- Database:
	- MySQL:
		- The MySQL database has been used to store faculty, publication, and university data. The MySQL Connector library was used to establish a connection and execute SQL queries for data retrieval and updates.
	- MongoDB:
		- MongoDB has been used to store faculty members' information and research summaries. The PyMongo library facilitated interactions with the MongoDB database, enabling the storage and retrieval of faculty-related data.
	- Neo4j:
		- Neo4j, a graph database, has been employed to store network data related to faculty collaborations. The Neo4j Connector library allowed the tool to interact with the Neo4j database and create faculty collaboration graphs.

In summary, the implementation process involved data integration from multiple data sources, such as MySQL, MongoDB, and Neo4j databases. The data was processed, filtered, and presented using Dash components, including drop-downs, graphs, and text areas. The interactive functionalities, such as searching by faculty name, university, or keyword, were realized through Dash's callback mechanism, enabling dynamic updates without page reloads. The integration of advanced features, including the OpenAI API and SERP API, aids in summarizing faculty information, identifying research trends, uncovering collaborations, and gaining valuable insights within the academic community.

<hr>

### Database Techniques
We have employed views, indexes, a constraint, a trigger, and prepared statements.

1. Views
We have created three views:
```kpi_faculty, kpi_publication, kpi_university```
These views provide essential statistics about the database, specifically the current size of faculty, publication, and university records in the “Current Database Size” section. These views are updated whenever the app.py runs.

2. Indexes
We have created an index ```university_name``` in the ```keyword_univ_final``` table. The index improves query performance when searching or filtering records in the university section.

3. Constraint and Trigger
We have implemented constraints and triggers to enforce a minimum length requirement for the `name` field within the `keyword` table. This stipulation mandates that the length of the keyword name must exceed 2 characters. A trigger named `update_word_count` automatically generates new data in the `word_count` column within the `keyword` table, preceding the insertion of a new row. These triggers and constraints collectively serve to hinder the insertion of meaningless records from the users in the update section.

4. Prepared Statements
We utilize prepared statements to execute parameterized queries. More specifically, we use prepared statements to dynamically retrieve data related to universities based on user-selected university names By leveraging prepared statements, we ensure a secure and efficient data interaction process, enhancing the overall user experience.

<hr>

### Extra-Credit Capabilities
In addition to the core functionalities, we have developed several extra-credit capabilities. The _four_ advanced features include:

1. **External Data Sourcing**: Google Scholars Integration for Comprehensive Research
To provide students with a broader perspective on academic research, we have integrated data from Google Scholars using the SERP API. This integration allows students to access up-to-date information about academic publications presenting the title of the publication along with an embedded hyperlink within it.

2. **Multi-database querying & 3. Data Expansion**: ChatGPT Summary for Simplified Data Comprehension
Our integration of ChatGPT helps students receive concise and easy-to-understand summaries since document data and network graphs are hard to grasp the information quickly. ChatGPT consolidates data from multiple sources, MongoDB and Neo4j, and freely summarizes key information by itself.

4. **Data Cleaning**: "Find Bugs?" Section
We have also included a 'Database Update' section in the bottom-right corner of the website, allowing users to report any incorrect or up-to-date information. This section requires the user to input the professor's name, which is used to match the corresponding records in the MongoDB database for updating. Users have the option to update the professor's name, position, phone number, and email address, all of which are sourced from MongoDB. The provided input will be used to update the MongoDB database accordingly.

<hr>

### Contributions:
The development of the University Explorer dashboard is a collaborative effort, and the following team members have contributed to this project:

| Name            | @hyeonjae-cho                  | @gaotianzheng              |
|-----------------|------------------------------|------------------------------|
| Working Hours   | 63 hours (approx)            | 20 hours (approx)            |
| Responsibilities| - Designed and implemented the Area and Professor sections of the dashboard, integrating data from MySQL and using Plotly for visualizations.<br>- Implemented additional capabilities: ChatGPT and Google Scholars for external data sourcing, multi-database querying, and data expansion.<br>- Developed the database update section to allow user bug input.<br>- Participated in creating a demo video to showcase the application's core features.| - Designed and implemented the University Section of the dashboard, integrating data from MySQL and presenting visualizations using Plotly.<br>- Collaborated with Hyeonjae Cho in reviewing and testing the overall functionality of the application.<br>- Authored the README file, providing project overview, technical details, feature documentation, and local setup instructions.<br>- Participated in creating a demo video to showcase the application's core features.|
