import pandas as pd
import numpy as np
from pymongo.mongo_client import MongoClient
from datetime import datetime
import asyncio
import time
import math
import json
import uuid
from kafka3 import KafkaConsumer, KafkaProducer
#from lob_data_functions import calculate_attributes

# --------------------------------------------------------------- #
# calculate attributes from the lob data
# --------------------------------------------------------------- #

class calculate_attributes():
    
    def __init__(self,lob_data):
        self.data = lob_data
        self.timestamp = lob_data["timestamp"]
        self.bids = lob_data["bids"]
        self.asks = lob_data["asks"]
        self.reduce_lob()
        self.calculate_spread()
        self.calculate_LDispersion()

    def reduce_lob(self):
        # Aggregate data (e.g., calculate the sum of the volumes in a interval of prices)

        # asks #
        asks_prices = [item[0] for item in self.asks]
        asks_volumes = [item[1] for item in self.asks]

        data_asks = pd.DataFrame({"prices":asks_prices,"volume":asks_volumes})
        data_asks = data_asks.apply(pd.to_numeric)

        self.data_asks = data_asks

        ## asks bins ##
        iqr =  data_asks["prices"].quantile(0.75) - data_asks["prices"].quantile(0.25)
        h = 2*iqr*(len(asks_prices)**(-1/2))
        bins = round((max(data_asks["prices"])-min(data_asks["prices"]))/h)

        # create intervals #
        data_asks["interval"] = pd.cut(data_asks["prices"],bins = bins)
        self.agg_asks = data_asks.groupby("interval").agg({"volume":["sum","mean","std"]})

        # Plot histogram of the aggregated values

        # bids #
        bids_prices = [item[0] for item in self.bids]
        bids_volumes = [item[1] for item in self.bids]

        data_bids = pd.DataFrame({"prices":bids_prices,"volume":bids_volumes})
        data_bids = data_bids.apply(pd.to_numeric)

        self.data_bids = data_bids

        ## bids bins ##
        iqr =  data_bids["prices"].quantile(0.75) - data_bids["prices"].quantile(0.25)
        h = 2*iqr*(len(bids_prices)**(-2/3))
        bins = round((max(data_bids["prices"])-min(data_bids["prices"]))/h)

        # create intervals #
        data_bids["interval"] = pd.cut(data_bids["prices"],bins = bins)
        self.agg_bids = data_bids.groupby("interval").agg({"volume":["sum","mean","std"]})

    def return_agg_bids(self):
        return self.agg_bids

    def return_agg_ask(self):
        return self.agg_asks

    def calculate_spread(self):
        self.spread = (float(self.asks[0][0]) - float(self.bids[0][0]))

    def calculate_LDispersion(self):

        ########
        ######## Order book dispersion:
        ########

        total_volume = sum(self.data_bids["volume"]) + sum(self.data_asks["volume"])

        # bids
        price_bids_t1 = (self.data_bids[1:])["prices"]
        price_bids_t = (self.data_bids[:-1])["prices"]

        # asks
        price_asks_t1 = (self.data_asks[1:])["prices"]
        price_asks_t = (self.data_asks[:-1])["prices"]

        # weights:
        ## bids:

        bids_weights = (self.data_bids[1:])["volume"]/total_volume
        bids_weights = np.where(bids_weights == 0, 0.00001, bids_weights)

        Dst_bids = np.array(price_bids_t) - np.array(price_bids_t1)
        Dst_bids = np.where(Dst_bids == 0, 0.00001, Dst_bids)

        Dispersion_Bids_numerador = sum(bids_weights*Dst_bids)
        Dispersion_Bids_denominador = sum(bids_weights)

        if Dispersion_Bids_denominador == 0:
            Dispersion_Bids_denominador = 0.00001

        Dispersion_Bids = Dispersion_Bids_numerador/Dispersion_Bids_denominador

        ## asks:

        asks_weights = (self.data_asks[1:])["volume"]/total_volume
        asks_weights = np.where(asks_weights == 0, 0.00001, asks_weights)

        Dst_asks = np.array(price_asks_t1) - np.array(price_asks_t)
        Dst_asks = np.where(Dst_asks == 0, 0.00001, Dst_asks)

        Dispersion_asks_numerador = sum(asks_weights*Dst_asks)
        Dispersion_asks_denominador = sum(asks_weights)
            
        if Dispersion_asks_denominador == 0:
            Dispersion_asks_denominador = 0.00001

        Dispersion_Asks = Dispersion_asks_numerador/Dispersion_asks_denominador

        # LDispersion = (Dispersion_Bids + Dispersion_asks)/2
        LDispersion =  (Dispersion_Bids + Dispersion_Asks)/2

        self.Dispersion_Bids = Dispersion_Bids
        self.Dispersion_Asks = Dispersion_Asks
        self.LDispersion = LDispersion

    def return_statistics(self):
        return json.dumps({"timestamp":self.timestamp,"spread":self.spread,"Bids dispersion":self.Dispersion_Bids,
        "Asks dispersion":self.Dispersion_Asks,"LDispersion":self.LDispersion})

# --------------------------------------------------------------- #
# sliding window 
# --------------------------------------------------------------- #

class sliding_window():

    def __init__(self):
        self.lobdata = None
        self.data = {}

    def new_lob(self,data):
        self.lobdata = data
    
    def get_lob(self):
        return self.lobdata

    def send_lob(self):
        # send json data 
        self.data["timestamp"] = math.floor(datetime.now().timestamp())
        self.data["bids"] = self.lobdata["bids"][0]
        self.data["asks"] = self.lobdata["asks"][0]
        return json.dumps(self.data)

async def run_sliding_window():
    
    conn_str = "mongodb+srv://erickchatalov:25e12c15r45f17@cluster0.8tszpip.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    time_lob = math.floor(datetime.now().timestamp())
    sw = sliding_window()

    while True:

        time_now = math.floor(datetime.now().timestamp())

        # ----------------------- #
        # save lob data #

        try:          
            sw.get_lob() != None
            if (time_now == (time_lob+10)):

                time_lob += 10

                clientdb = MongoClient(conn_str, serverSelectionTimeoutMS=5000)
                lobdata = pd.DataFrame(clientdb.BTCEUR.LimitOrderBook.find({}).sort({"_id":-1}).limit(1)) .drop("_id",axis=1)
                clientdb.close()

                sw.new_lob(lobdata)

                # calculate the statistics from the lob data #
                attr = calculate_attributes(json.loads(sw.send_lob()))

                print(attr.return_statistics())                
                # post to kafka #
                try:
                    producer = KafkaProducer(bootstrap_servers="ed-kafka:29092")
                    producer.send('lob-data', key=bytes(str(uuid.uuid4()), 'utf-8'), value= bytes( str( attr.return_statistics() ),'utf-8' ))
                    producer.close()
                except:
                    pass

        except:
            sw.new_lob(time_lob)

            # calculate the statistics from the lob data #
            attr = calculate_attributes(json.loads(sw.send_lob()))
            
            print(attr.return_statistics())

            # post to kafka #
            try:
                producer = KafkaProducer(bootstrap_servers="ed-kafka:29092")
                producer.send('lob-data', key=bytes(str(uuid.uuid4()), 'utf-8'), value= bytes( str( attr.return_statistics() ),'utf-8' ))
                producer.close()
            except:
                pass

        time.sleep(0.1)
        # ------------- #

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_sliding_window())

while True:
    try: 
        main()
    except:
        continue
