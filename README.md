# Stay Present (aka please.staypres.net)

A workflow for educators to store and analyze data about student attendance and engagement based on communications between students' internet devices and advanced Meraki routers/API's.  

## Stack
* Node-Red Services to easily consume the Meraki Router Dashboard and Scanner API's to store network client data on a mongodb database (Hosted by mlab).
* A Plotly Dash website that consumes Meraki data from the mongodb databases and produces interactive visualization of the data.

## Demo!

http://please.staypres.net

The data in this website is continuously aggregated data from Meraki Routers distributed all about the CalHacks venue in Memorial Stadium, Berkeley, CA. Dashboards show metrics on how long "students" (University Hackers) were present in the venue, due to their wireless communications with the routers, and the internet traffic they produed throughout the hackathon.

