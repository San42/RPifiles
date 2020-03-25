import psycopg2
conn = psycopg2.connect("dbname=sensor_data user=postgres password=15cs420 host=localhost")
cur=conn.cursor()
#cur.execute("insert into ne_boiler_test values (%s,%s,%s,%s,%s,%s)",('15101234','76.87','2020-02018T15:26:56.43','Temperature','F','0'))
cur.execute("alter table ne_boiler_test add column published text")
conn.commit()

