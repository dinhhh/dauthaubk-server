## Flask server for DauThauBK mobile application
A simple server using Flask for searching, receiving information about bidding field. The data is crawled from [muasamcong website](http://muasamcong.mpi.gov.vn/) using [my Scrapy Bot](https://github.com/dinhhh/dauthaubk-spider)  

### FE project can be found in [this repository](https://github.com/dinhhh/dauthaubk-frontend)

### Setup

1. Clone this repository
> `git clone https://github.com/dinhhh/dauthaubk-server`
2. Init virtual python environment and activate it
> `python -m venv venv`
> 
> `source /venv/bin/activate`
3. Install requirements
> `pip install -r requirements.txt`
3. Change MONGO_URI in app config (app.py file) to your mongo path (for example: localhost:27017)
4. Run server
> `python app.py`
5. Swagger UI is available [at link](http://192.168.1.12:5000/swagger/) after run server

## Author
HungND - 20183548 - dinhhung.0115@gmail.com