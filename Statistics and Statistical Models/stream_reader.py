from kafka3 import KafkaConsumer, KafkaProducer

consumer = KafkaConsumer(bootstrap_servers="ed-kafka:29092")
consumer.subscribe(['sliding_window'])

try:
    while True:
        msgs = consumer.poll(timeout_ms=10)
        if (msgs == {}):
            pass
        else:
            print(msgs)        
finally:
    consumer.close()