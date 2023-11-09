import csv
from datetime import datetime
from linebot.models import TextSendMessage

from server.gcs_helper import GcsHelper


def send_message_linebot(line_bot_api, event, text):
     user_id = event.source.user_id
     message = TextSendMessage(text=text)
     line_bot_api.push_message(user_id, message)


def build_single_row_data(scrapper):
     twii = scrapper.get_TWII_data()
     tw_future = scrapper.get_TW_Future()
     sox = scrapper.get_SOX_data()
     tsmc = scrapper.get_TSMC_data()
     usd = scrapper.get_USD_Index_data()
     jpy = scrapper.get_JPY_Index_data()
     return {
          "date": datetime.now().strftime("%Y/%m/%d"),
          "大盤_開盤價": twii['開盤'], "大盤_最高價": twii['最高'], "大盤_最低價": twii['最低'], "大盤_收盤價": twii['收盤'],
          "自營商": tw_future['自營商'], "投信": tw_future['投信'], "外資": tw_future['外資'],
          "費半_開盤價": sox['開盤'], "費半_最高價": sox['最高'], "費半_最低價": sox['最低'], "費半_收盤價": sox['收盤'],
          "台積_開盤價": tsmc['開盤'], "台積_最高價": tsmc['最高'], "台積_最低價": tsmc['最低'], "台積_收盤價": tsmc['收盤'],
          "美元_開盤價": usd['開盤'], "美元_最高價": usd['最高'], "美元_最低價": usd['最低'], "美元_收盤價": usd['指數'],
          "日圓_開盤價": jpy['開盤'], "日圓_最高價": jpy['最高'], "日圓_最低價": jpy['最低'], "日圓_收盤價": jpy['指數']
     }


def append_row_to_gcs_file(bucket_name, blob_name, row_data):
     file_path = 'data/mock_sql.csv'
     gcs_helper = GcsHelper()
     gcs_helper.download_file_from_bucket(bucket_name, blob_name, file_path)

     with open(file_path, 'a', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=row_data.keys())
        writer.writerow(row_data)

     gcs_helper.upload_file_to_bucket(bucket_name, blob_name, file_path)


def predict(model):
    input_data =[[[0.10141737, 0.04451055, 0.00903744, 0.33245956, 0.33114825,
         0.33269302, 0.53941869, 0.46687782, 0.47152187, 0.21658305,
         0.46347709, 0.47077411, 0.4652609 , 0.47360927, 0.6926213 ,
         0.42254164, 0.42474625, 0.4233871 , 0.42181376, 0.62653933,
         0.63409458, 0.68251451, 0.68149114, 0.67677946, 0.6883424 ,
         0.67136584, 0.6729736 , 0.3481476 , 0.40568302, 0.41287534,
         0.42757112, 0.38912224, 0.40114405, 0.3876575 ],
        [0.10116807, 0.04390312, 0.00858655, 0.32938886, 0.32324377,
         0.33365349, 0.53941869, 0.46561921, 0.4703063 , 0.19995584,
         0.46583502, 0.46753695, 0.465942  , 0.46944062, 0.6926213 ,
         0.42270765, 0.42586193, 0.42043011, 0.42289499, 0.62712574,
         0.63553782, 0.68661268, 0.68757545, 0.67911319, 0.68668716,
         0.66974809, 0.67460874, 0.3481476 , 0.40495317, 0.40896814,
         0.41807568, 0.39399942, 0.39270512, 0.38863465],
        [0.10111437, 0.0437996 , 0.00899235, 0.33979928, 0.33140037,
         0.33646103, 0.53941869, 0.46576174, 0.46647395, 0.22133788,
         0.46068347, 0.4675473 , 0.45963348, 0.46397785, 0.6926213 ,
         0.42351004, 0.42490952, 0.42432796, 0.42573321, 0.62771216,
         0.63468885, 0.68688101, 0.68462987, 0.66184364, 0.67486403,
         0.66928588, 0.67717823, 0.3481476 , 0.40827516, 0.4093985 ,
         0.43839284, 0.41414565, 0.41387834, 0.40543181],
        [0.10094178, 0.04374296, 0.00878455, 0.34002397, 0.32617778,
         0.33949021, 0.53941869, 0.46637131, 0.46620652, 0.21579014,
         0.46898816, 0.47321216, 0.46738035, 0.46804879, 0.6926213 ,
         0.42501798, 0.42640616, 0.42930108, 0.42884174, 0.632571  ,
         0.63638679, 0.68631995, 0.68255348, 0.66091015, 0.66658785,
         0.65218396, 0.65965896, 0.3481476 , 0.41102408, 0.41203241,
         0.43666843, 0.42167786, 0.42056313, 0.41336761],
        [0.10088617, 0.04392265, 0.00898647, 0.33777711, 0.33068002,
         0.34118951, 0.53941869, 0.4673146 , 0.46577833, 0.19363254,
         0.47226875, 0.47648038, 0.46801646, 0.47351292, 0.6926213 ,
         0.42691329, 0.42773953, 0.42701613, 0.42938235, 0.63173327,
         0.63961287, 0.68385617, 0.67753151, 0.65110852, 0.66114921,
         0.64825514, 0.65802383, 0.3481476 , 0.41466231, 0.41983529,
         0.45288733, 0.43247902, 0.42966823, 0.42384811],
        [0.10058317, 0.04365897, 0.00877279, 0.33920012, 0.33158046,
         0.3450314 , 0.53941869, 0.46848919, 0.46897437, 0.19399963,
         0.479231  , 0.48152209, 0.47408549, 0.47627676, 0.6926213 ,
         0.42876709, 0.42874636, 0.42836022, 0.4312745 , 0.63056044,
         0.63783004, 0.68283163, 0.6734753 , 0.6571762 , 0.66162213,
         0.64709961, 0.64938099, 0.3481476 , 0.41666334, 0.42254973,
         0.44048801, 0.42552924, 0.4268904 , 0.42828009],
        [0.09998677, 0.04365897, 0.00858655, 0.33111144, 0.32185564,
         0.3357222 , 0.53941869, 0.4678481 , 0.46892139, 0.2049643 ,
         0.46557387, 0.47264422, 0.47103229, 0.4793064 , 0.6926213 ,
         0.43015052, 0.43035185, 0.42836022, 0.42911204, 0.62989026,
         0.6387639 , 0.6845392 , 0.67077116, 0.66604434, 0.67037125,
         0.65541946, 0.65498715, 0.3481476 , 0.41852417, 0.4278531 ,
         0.44331226, 0.42110855, 0.41754353, 0.41680954],
        [0.09968377, 0.04345389, 0.00878651, 0.33994907, 0.32574557,
         0.3391208 , 0.53941869, 0.46767524, 0.47267913, 0.20974582,
         0.47846211, 0.47945945, 0.47578549, 0.47423446, 0.6926213 ,
         0.43073156, 0.4309505 , 0.42715054, 0.43032842, 0.63123063,
         0.63944308, 0.68107528, 0.66893621, 0.64760793, 0.65878458,
         0.65310839, 0.66316281, 0.3481476 , 0.41960393, 0.42983859,
         0.44784101, 0.43290928, 0.43123976, 0.43246198],
        [0.0998065 , 0.04363553, 0.00896687, 0.33964949, 0.32819478,
         0.33712597, 0.53941869, 0.46821776, 0.47418082, 0.17700133,
         0.47967086, 0.48421616, 0.47741211, 0.48247542, 0.6926213 ,
         0.43168613, 0.43149473, 0.4297043 , 0.42978781, 0.63139817,
         0.63825452, 0.67802605, 0.66792216, 0.6462077 , 0.65452826,
         0.64317079, 0.64564354, 0.3481476 , 0.42135943, 0.43358787,
         0.45450971, 0.42148372, 0.42882459, 0.42529965]]]
    prediction = model.predict(input_data)
    reply_text = f"Predicted value: {prediction[0][0]}"
    return reply_text